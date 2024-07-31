document.addEventListener('DOMContentLoaded', function () {
    const menuToggleBtn = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
  
    menuToggleBtn.addEventListener('click', function () {
        mobileMenu.classList.toggle('open');
    });

    function toggleMenu() {
        if (mobileMenu.classList.contains('open')) {
            mobileMenu.classList.remove('open');
        } else {
            mobileMenu.classList.add('open');
        }
    }

    // 문서 클릭 시 메뉴 닫기
    document.addEventListener('click', function(event) {
        if (event.target !== mobileMenu && event.target !== menuToggleBtn) {
            mobileMenu.classList.remove('open');
        }
    });
});
