/*
Name: Mann Mihir Desai
Purpose: Validate raffle input and determine prize eligibility
*/

document.getElementById("surveyForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const raffleInput = document.getElementById("raffle").value;
  const numbers = raffleInput.split(",").map(n => parseInt(n.trim()));

  // Validate count
  if (numbers.length < 10) {
    window.location.href = "error.html";
    return;
  }

  // Validate range
  for (let n of numbers) {
    if (isNaN(n) || n < 1 || n > 100) {
      window.location.href = "error.html";
      return;
    }
  }

  const sum = numbers.reduce((a, b) => a + b, 0);
  const avg = sum / numbers.length;

  if (avg > 50) {
    alert("🎉 Congratulations! You won a free movie ticket!");
  } else {
    alert("Thank you for participating in the survey.");
  }

  this.reset();
});
