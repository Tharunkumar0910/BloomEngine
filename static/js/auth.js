/**
 * BloomEngine - Authentication Page JavaScript
 * Frontend logic for tab switching, password toggles, form validation, and dashboard redirection.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const tabButtons = document.querySelectorAll('.auth-tab-btn');
  const authViews = document.querySelectorAll('.auth-view');
  const passwordToggles = document.querySelectorAll('.btn-toggle-password');
  const signInForm = document.getElementById('signInForm');
  const createAccountForm = document.getElementById('createAccountForm');
  const socialButtons = document.querySelectorAll('.btn-social');

  // 1. Tab Switcher Logic
  function switchTab(targetTabId) {
    tabButtons.forEach(btn => {
      if (btn.dataset.tab === targetTabId) {
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
      }
    });

    authViews.forEach(view => {
      if (view.id === targetTabId) {
        view.classList.add('active');
      } else {
        view.classList.remove('active');
      }
    });
  }

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      switchTab(btn.dataset.tab);
    });
  });

  // Switch tabs from inline links (e.g. "Create an account" link)
  document.querySelectorAll('.switch-tab-link').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const target = link.dataset.target;
      if (target) {
        switchTab(target);
      }
    });
  });

  // 2. Password Show / Hide Toggle
  passwordToggles.forEach(toggleBtn => {
    toggleBtn.addEventListener('click', () => {
      const inputId = toggleBtn.dataset.for;
      const input = document.getElementById(inputId);
      if (input) {
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';

        // Toggle icon path
        const svgPath = toggleBtn.querySelector('path');
        if (svgPath) {
          if (isPassword) {
            // Slash eye icon (hidden)
            svgPath.setAttribute('d', 'M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.261A7.957 7.957 0 0110 5c3.54 0 6.57 2.28 7.6 5.5a7.978 7.978 0 01-2.18 3.398l-1.48-1.48A3.001 3.001 0 0010.5 8.52L7.968 6.554zM10 15a5 5 0 01-5-5c0-.8.19-1.55.53-2.22L4.01 6.26A9.972 9.972 0 00.458 10c1.274 4.057 5.064 7 9.542 7 1.63 0 3.16-.39 4.51-1.07l-1.78-1.78A7.95 7.95 0 0110 15z');
          } else {
            // Normal eye icon
            svgPath.setAttribute('d', 'M10 12a2 2 0 100-4 2 2 0 000 4z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z');
          }
        }
      }
    });
  });

  // 3. Helper to simulate form submission & navigate to Dashboard
  function handleFormSubmit(event, formElement, submitButton) {
    event.preventDefault();

    if (!formElement.checkValidity()) {
      formElement.reportValidity();
      return;
    }

    const spinner = submitButton.querySelector('.spinner');
    const btnText = submitButton.querySelector('.btn-text');

    if (spinner) spinner.style.display = 'inline-block';
    if (btnText) btnText.textContent = 'Authenticating...';
    submitButton.disabled = true;

    // Simulate smooth auth response and navigate to /dashboard
    setTimeout(() => {
      if (btnText) btnText.textContent = 'Success! Redirecting...';
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 400);
    }, 700);
  }

  if (signInForm) {
    signInForm.addEventListener('submit', (e) => {
      const submitBtn = signInForm.querySelector('button[type="submit"]');
      handleFormSubmit(e, signInForm, submitBtn);
    });
  }

  if (createAccountForm) {
    createAccountForm.addEventListener('submit', (e) => {
      const pass = document.getElementById('regPassword');
      const confirmPass = document.getElementById('regConfirmPassword');

      if (pass && confirmPass && pass.value !== confirmPass.value) {
        e.preventDefault();
        confirmPass.setCustomValidity('Passwords do not match.');
        confirmPass.reportValidity();
        return;
      } else if (confirmPass) {
        confirmPass.setCustomValidity('');
      }

      const submitBtn = createAccountForm.querySelector('button[type="submit"]');
      handleFormSubmit(e, createAccountForm, submitBtn);
    });
  }

  // 4. Social Buttons (Google / Microsoft Placeholder)
  socialButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      // Show brief visual feedback and navigate to dashboard for seamless prototype testing
      const originalText = btn.innerHTML;
      btn.innerHTML = `<span style="font-size:0.85rem; font-weight:600; color:var(--primary)">Redirecting with OAuth...</span>`;
      setTimeout(() => {
        window.location.href = '/dashboard';
      }, 500);
    });
  });
});
