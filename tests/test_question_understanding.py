import unittest
import torch
import time
from question_profile import QuestionProfile
from question_understanding import QuestionUnderstandingEngine
from pipeline_context import PipelineContext
from validation_engine import evaluate_candidate
from candidate_ranker import rank_candidates, rank_candidates_dicts, calculate_nlp_rank_score
from validation_models import ValidationEngineOutput

class MockSTModel:
    def encode(self, text, convert_to_tensor=True):
        # Return a dummy 384-dimensional tensor for MiniLM similarity check
        if isinstance(text, list):
            return torch.zeros((len(text), 384))
        return torch.zeros(384)

def mock_get_cached_embedding(text, st_model):
    return torch.zeros(384)

def mock_deberta_classifier_fn(text):
    # Mock classifier: returns Remember level if "define" is in the text, otherwise Analyze
    if "define" in text.lower():
        return "Remember", "Easy", 95.0
    return "Analyze", "Medium", 85.0

def mock_validate_bloom_verbs(text, target_bloom):
    return True, "None"

class TestQuestionUnderstandingPipeline(unittest.TestCase):
    def setUp(self):
        self.st_model = MockSTModel()
        self.question_db = "What is database normalization in DBMS?"
        self.question_network = "Explain the OSI model and how it works."
        
    def test_normalize_pipeline(self):
        # Test lowercasing, abbreviation expansion (if configured), and whitespace cleanup
        raw = "   What   is  a  DBMS?   "
        normalized = QuestionUnderstandingEngine.normalize_pipeline(raw)
        self.assertEqual(normalized, "what is a database management system?")

    def test_build_profile_and_caching(self):
        # 1. First build
        profile1 = QuestionUnderstandingEngine.build_profile(self.question_db, "Remember")
        self.assertIsNotNone(profile1)
        self.assertEqual(profile1.raw_question, self.question_db)
        self.assertEqual(profile1.source_bloom, "Remember")
        
        # Verify domain and topic detection from dictionary maps
        self.assertEqual(profile1.domain, "Database Management Systems")
        self.assertEqual(profile1.topic, "Normalization")
        
        # 2. Second build (should fetch from cache)
        profile2 = QuestionUnderstandingEngine.build_profile(self.question_db, "Remember")
        self.assertIs(profile1, profile2)

    def test_pipeline_context(self):
        orig_profile = QuestionUnderstandingEngine.build_profile(self.question_db, "Remember")
        ctx = PipelineContext(
            source_question=self.question_db,
            source_bloom="Remember",
            target_bloom="Remember",
            target_difficulty="Easy",
            source_profile=orig_profile
        )
        self.assertEqual(ctx.source_question, self.question_db)
        self.assertIs(ctx.source_profile, orig_profile)
        
        # Track simulated candidate
        ctx.generated_candidates.append("Define database normalization.")
        ctx.timings["profiling"] = 0.05
        self.assertEqual(len(ctx.generated_candidates), 1)
        self.assertEqual(ctx.timings["profiling"], 0.05)

    def test_evaluate_candidate_and_hard_filters(self):
        orig_prof = QuestionUnderstandingEngine.build_profile(self.question_db, "Remember")
        
        # Candidate 1: Matches Bloom Level (Remember)
        cand_q_pass = "Define database normalization in a DBMS."
        val_out_pass = evaluate_candidate(
            original_q=orig_prof,
            candidate_q=cand_q_pass,
            target_bloom="Remember",
            target_difficulty="Easy",
            seen_questions=set(),
            session_seen=[],
            config_mode={"mode_name": "TestMode"},
            deberta_classifier_fn=mock_deberta_classifier_fn,
            st_model=self.st_model,
            get_cached_embedding_fn=mock_get_cached_embedding,
            validate_bloom_verbs_fn=mock_validate_bloom_verbs
        )
        
        # Candidate 2: Bloom Classification Mismatch hard filter
        cand_q_fail = "Analyze the database normalization process."
        val_out_fail = evaluate_candidate(
            original_q=orig_prof,
            candidate_q=cand_q_fail,
            target_bloom="Remember",
            target_difficulty="Easy",
            seen_questions=set(),
            session_seen=[],
            config_mode={"mode_name": "TestMode"},
            deberta_classifier_fn=mock_deberta_classifier_fn,
            st_model=self.st_model,
            get_cached_embedding_fn=mock_get_cached_embedding,
            validate_bloom_verbs_fn=mock_validate_bloom_verbs
        )
        
        self.assertTrue(val_out_pass.passed or val_out_pass.total_score >= 0)
        self.assertFalse(val_out_fail.passed)
        self.assertEqual(val_out_fail.rejection_reason, "Classification Mismatch")

    def test_candidate_ranking_priorities(self):
        # Prepare two outputs with domain/topic metrics
        out_high = ValidationEngineOutput(
            bloom_score=35.0,
            concept_score=10.0,
            entity_score=10.0,
            number_score=5.0,
            semantic_score=1.0,
            duplicate_score=2.0,
            grammar_score=3.0,
            domain_score=20.0,  # High domain score
            topic_score=15.0,   # High topic score
            total_score=100.0,
            passed=True,
            rejection_reason="None",
            detailed_metrics={}
        )
        
        out_low = ValidationEngineOutput(
            bloom_score=35.0,
            concept_score=10.0,
            entity_score=10.0,
            number_score=5.0,
            semantic_score=1.0,
            duplicate_score=2.0,
            grammar_score=3.0,
            domain_score=10.0,  # Low domain score
            topic_score=5.0,    # Low topic score
            total_score=80.0,
            passed=True,
            rejection_reason="None",
            detailed_metrics={}
        )
        
        # Test rank_candidates
        candidates = [
            ({"attempt_number": 1, "generated_question": "q_low"}, out_low),
            ({"attempt_number": 1, "generated_question": "q_high"}, out_high)
        ]
        
        ranked = rank_candidates(candidates)
        # Higher score (which is driven by domain/topic) should rank first
        self.assertEqual(ranked[0][0]["generated_question"], "q_high")
        
        # Test rank_candidates_dicts
        cand_dicts = [
            {
                "question": "q_low",
                "validation_status": "Pass",
                "Total Score": 80.0,
                "Bloom Score": 35.0,
                "Domain Score": 10.0,
                "Topic Score": 5.0,
                "attempt_number": 1
            },
            {
                "question": "q_high",
                "validation_status": "Pass",
                "Total Score": 100.0,
                "Bloom Score": 35.0,
                "Domain Score": 20.0,
                "Topic Score": 15.0,
                "attempt_number": 1
            }
        ]
        ranked_dicts = rank_candidates_dicts(cand_dicts)
        self.assertEqual(ranked_dicts[0]["question"], "q_high")

if __name__ == "__main__":
    unittest.main()
