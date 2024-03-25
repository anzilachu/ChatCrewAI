document.addEventListener('DOMContentLoaded', function() {
    const characterCards = document.querySelectorAll('.character-card');
  
    characterCards.forEach(card => {
      card.addEventListener('click', function() {
        const characterName = card.getAttribute('data-character');
        alert(`You clicked on ${characterName}`);
        // You can replace the alert with logic to start a chat with the selected character
      });
    });
  });
  