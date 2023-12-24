document.getElementById("toggle-password").addEventListener("click", function () {
    const passwordInput = document.getElementById("password");
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }

});

// Beginning Of Typing JavaScript

const dynamicTxt = document.querySelector(".dynamic-txt");
const blinkingCursor = document.querySelector(".blinking-cursor");
const text = ["Hand Companion is a cutting-edge technology designed to bridge the communication gap by translating sign language into text and speech. With Hand Companion's advanced AI algorithms, individuals can effortlessly communicate their thoughts and feelings through sign language, ensuring that everyone, regardless of their hearing abilities, is understood. This innovative solution not only fosters inclusivity but also empowers the deaf and hard-of-hearing community to engage in everyday conversations seamlessly."];

let maxWidth = 0;
text.forEach(line => {
  const lineWidth = line.length * 10;
  if (lineWidth > maxWidth) {
    maxWidth = lineWidth;
  }
});
dynamicTxt.style.width = `${maxWidth}px`;

let wordIndex = 0;
let txtIndex = 0;
let isDeleting = false;
let delay = 40;

typeWords();

function typeWords() {
  const currentWordIndex = wordIndex % text.length;
  const currentWord = text[currentWordIndex];

  if (!isDeleting) {
    dynamicTxt.textContent = currentWord.substring(0, txtIndex);
    txtIndex++;

    if (txtIndex > currentWord.length) {
      isDeleting = true;
      delay = 1000;
    }
  } else {
    dynamicTxt.textContent = currentWord.substring(0, txtIndex);
    txtIndex--;

    if (txtIndex === 0) {
      isDeleting = false;
      wordIndex++;
      delay = 200;
    }
  }
  blinkingCursor.style.display = "none";

  setTimeout(typeWords, delay);
}