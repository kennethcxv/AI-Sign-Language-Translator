document.addEventListener('DOMContentLoaded', function () {
  const sphereContainer = document.getElementById('sphereContainer');
  const tags = [
    'Communication',
    'Solutions',
    'Businesses',
    'Educational',
    'Institutions',
    'Organizers',
    'Nonverbal',
    'Finger movements',
    'Visual language',
    'Alphabet',
    'Hearing-impaired',
    'Interpreter',
    'Dedicated',
    'Strong',
    'Willful',
    'Unique',
    'Identity',
    'Creative',
    'Outstanding',
    'Loving',
    'Caring',
  ];

  const options = {
    radius: 250,
    maxSpeed: 15.0,
    minSpeed: 2.0,
    direction: 135,
    keep: true,
    color: '#000000'  // Set the color of the words in the sphere to black
  };

  TagCloud(sphereContainer, tags, options);

  let prevScrollpos = window.pageYOffset;
  window.onscroll = function () {
    const currentScrollPos = window.pageYOffset;
    if (prevScrollpos > currentScrollPos) {
      document.querySelector('header').style.transform = 'translateY(0)';
    } else {
      document.querySelector('header').style.transform = 'translateY(-100%)';
    }
    prevScrollpos = currentScrollPos;
  };
});
