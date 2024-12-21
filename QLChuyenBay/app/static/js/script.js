const airlineLogos = document.querySelectorAll('.airline-logo');
airlineLogos.forEach(logo => {
    const button = document.createElement('button');
    button.classList.add('find-flights-btn');
    button.textContent = 'Tìm chuyến bay';
    logo.appendChild(button);
});