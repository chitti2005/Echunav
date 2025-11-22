(function () {
  // If timer element not present, do nothing.
  const timerEl = document.getElementById('timer');
  if (!timerEl) return;

  let timeLeft = 20; // seconds
  const submitBtn = document.querySelector('button[type="submit"]');

  function updateDisplay() {
    timerEl.textContent = timeLeft;
    if (timeLeft <= 5) {
      timerEl.classList.add('text-danger');
    }
  }

  updateDisplay();
  const interval = setInterval(() => {
    timeLeft -= 1;
    updateDisplay();
    if (timeLeft <= 0) {
      clearInterval(interval);
      if (submitBtn) submitBtn.disabled = true;
      alert('Session expired. Please log in again to vote.');
      // redirect to logout route (Flask will clear session)
      window.location.href = '/logout';
    }
  }, 1000);
})();
