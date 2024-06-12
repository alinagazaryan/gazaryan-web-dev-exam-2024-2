let deleteUserModal = document.querySelector('#deleteBook')

function getLoopAttributeOnClick() {
    return new Promise((resolve, reject) => {
        document.querySelectorAll('button').forEach(function(n) {
            n.addEventListener('click', function(e) {
                resolve(e.target.getAttribute('id'));
            });
        });
    });
}

deleteUserModal.addEventListener('show.bs.modal', function(event){
    getLoopAttributeOnClick().then(loopValue => {
        let form = document.querySelector('form')
        form.action = event.relatedTarget.dataset.url;
        let book_items = [];
        document.querySelectorAll('td').forEach(function(item) {
            if (item.getAttribute('id') !== null && item.getAttribute('id') === 'nameOfBook') {
                book_items.push(item)
            }
        });
        document.querySelectorAll('button').forEach(function(elem) {
            if (Number(elem.getAttribute('id')) == Number(loopValue)) {
                document.getElementById('bookName').innerHTML = book_items[loopValue - 1].textContent
            }
        });
    });
})

