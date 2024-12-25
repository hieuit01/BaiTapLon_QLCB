async function thanhToan() {
    const form = document.getElementById('form-thanh-toan');
    const pttt = form.querySelector('input[name="pttt"]:checked').value;

    const response = await fetch('/thanh-toan/' + maDatVe, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            pttt: pttt
        })
    });

    const result = await response.json();

    if (response.ok) {
        alert(result.message);
        // Thực hiện điều hướng hoặc các hành động khác khi thanh toán thành công
        window.location.href = '/';
    } else {
        alert(result.message);
    }
}

// Gọi hàm thanh toán khi người dùng gửi form
document.getElementById('form-thanh-toan').addEventListener('submit', function(e) {
    e.preventDefault();
    thanhToan();
});
