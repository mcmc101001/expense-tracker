const hiddenObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        }
        else {
            entry.target.classList.remove('show');
        }
    });
});

const hiddenEleObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show-ele');
        }
        else {
            entry.target.classList.remove('show-ele');
        }
    });
});

const hiddenElements = document.querySelectorAll('.hidden');
const hiddenTabElements = document.querySelectorAll('.hidden-ele');
hiddenElements.forEach((el) => hiddenObserver.observe(el));
hiddenTabElements.forEach((el) => hiddenEleObserver.observe(el));

document.querySelector('#hide_filters').onclick = () => {
    let filters = document.querySelector('.filters');
    let wrapper = document.querySelector('.wrapper');
    filters.style.animationPlayState = 'running';
    wrapper.style.animationPlayState = 'running';
    filters.addEventListener('animationend', () => {
        filters.style.display = 'none';
    });
}

document.querySelectorAll('.filter-checkbox').forEach((el) => {
    el.onclick = () => {
        const filterType = el.dataset.type;
        if (el.checked == 1){
            document.querySelectorAll(`.expense-type-${filterType}`).forEach((expense) => {
                expense.style.display = 'grid';
            })
        }
        else {
            document.querySelectorAll(`.expense-type-${filterType}`).forEach((expense) => {
                expense.style.display = 'none';
            })
        }
    }
});
