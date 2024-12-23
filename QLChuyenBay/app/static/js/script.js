const airlineLogos = document.querySelectorAll('.airline-logo');
const searchButton = document.querySelector('.search-button');

airlineLogos.forEach(logo => {
    logo.addEventListener('mouseover', () => {
        searchButton.style.display = 'block';
    });

    logo.addEventListener('mouseout', () => {
        searchButton.style.display = 'none';
    });
});