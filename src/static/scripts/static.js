const selectAllCheckbox = document.getElementById('selectAll');
const productCheckboxes = Array.from(document.getElementsByClassName('product-checkbox'));
const variantCheckboxes = Array.from(document.getElementsByClassName('variant-checkbox'));

const modal = document.getElementById('myModal');
const modalBody = document.getElementById('modalBody');
const discountButton = document.getElementById('discountButton');
const revertButton = document.getElementById('revertButton')
const closeButton = document.getElementById('closeButton');
const submitButton = document.getElementById('submitButton');

const discountTypeSelect = document.getElementById('discountType');
const discountValueInput = document.getElementById('discountValue');

const revertModal = document.getElementById('revertModal');
const revertForm = document.getElementById('revertForm');
const revertVariantIdInput = document.getElementById('revertVariantIdInput');
const revertSubmitButton = document.getElementById('revertSubmitButton');

// Xử lý sự kiện khi checkbox all thay đổi
selectAllCheckbox.addEventListener('change', function() {
    const isChecked = selectAllCheckbox.checked;
    productCheckboxes.forEach(function(checkbox) {
        checkbox.checked = isChecked;
    });
    variantCheckboxes.forEach(function(checkbox) {
        checkbox.checked = isChecked;
    });
    updateButtonStatus();
});

// Xử lý sự kiện khi checkbox product thay đổi
productCheckboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        const isChecked = checkbox.checked;
        updateVariantCheckboxes(checkbox, isChecked);
        updateButtonStatus();
        updateSelectAllCheckbox();
    });
});

// Xử lý sự kiện khi checkbox variant thay đổi
variantCheckboxes.forEach(function(checkbox) {
    checkbox.addEventListener('change', function() {
        const productId = checkbox.dataset.productId;
        const productCheckbox = document.getElementById(`productCheckbox_${productId}`);
        updateProductCheckbox(productCheckbox);
        updateButtonStatus();
        updateSelectAllCheckbox();
    });
});

// Cập nhật trạng thái của các checkbox variant dựa trên checkbox product tương ứng
function updateVariantCheckboxes(productCheckbox, isChecked) {
    const productId = productCheckbox.dataset.productId;
    const variantCheckboxes = Array.from(document.querySelectorAll(`.variant-checkbox[data-product-id="${productId}"]`));
    variantCheckboxes.forEach(function(variantCheckbox) {
        variantCheckbox.checked = isChecked;
    });
}

// Cập nhật trạng thái của checkbox product dựa trên trạng thái của các checkbox variant
function updateProductCheckbox(productCheckbox) {
    const productId = productCheckbox.dataset.productId;
    const variantCheckboxes = Array.from(document.querySelectorAll(`.variant-checkbox[data-product-id="${productId}"]`));
    const isProductChecked = variantCheckboxes.every(function(checkbox) {
        return checkbox.checked;
    });
    productCheckbox.checked = isProductChecked;
}

// Cập nhật trạng thái của checkbox all trên th dựa trên trạng thái của các checkbox product và variant
function updateSelectAllCheckbox() {
    const isAllChecked = productCheckboxes.every(function(checkbox) {
        return checkbox.checked;
    });
    const isAnyVariantUnchecked = variantCheckboxes.some(function(checkbox) {
        return !checkbox.checked;
    });
    selectAllCheckbox.checked = isAllChecked && !isAnyVariantUnchecked;
}

// Cập nhật trạng thái của nút
function updateButtonStatus() {
    const isAnyCheckboxChecked = productCheckboxes.some(function(checkbox) {
        return checkbox.checked;
    });

    const isAnyVariantChecked = variantCheckboxes.some(function(checkbox) {
        return checkbox.checked;
    });

    if (isAnyCheckboxChecked || isAnyVariantChecked) {
        discountButton.disabled = false;
        revertButton.disabled = false;
    } else {
        discountButton.disabled = true;
        revertButton.disabled = true;
    }
}

discountButton.addEventListener('click', function() {
    const selectedVariants = getSelectedVariants();
    updateModalContent(selectedVariants);
    showModal();
});

submitButton.addEventListener('click', function() {
    const selectedVariants = getSelectedVariants();
    hideModal();
});

// Lấy danh sách các variant đã chọn
function getSelectedVariants() {
    const selectedVariants = [];
    variantCheckboxes.forEach(function(checkbox) {
        if (checkbox.checked) {
            selectedVariants.push(checkbox.value);
        }
    });
    return selectedVariants;
}

function updateModalContent(selectedVariants) {
    const variantIdInput = document.getElementById('variantIdInput');
    variantIdInput.value = selectedVariants.join(',');
}

// Hiển thị modal
function showModal() {
    const myModal = new bootstrap.Modal(document.getElementById('myModal'));
    myModal.show();
}

// Ẩn modal
closeButton.addEventListener('click', function() {
    hideModal();
});

// Ẩn modal
function hideModal() {
    const myModal = document.getElementById('myModal');
    const bootstrapModal = bootstrap.Modal.getInstance(myModal);
    bootstrapModal.hide();
}

discountTypeSelect.addEventListener('change', function() {
    const selectedOption = discountTypeSelect.value;

    if (selectedOption === 'percent') {
        discountValueInput.min = '';
        discountValueInput.max = 99;
        discountValueInput.step = '0.01';
    } else {
        discountValueInput.min = 1;
        discountValueInput.max = '';
        discountValueInput.step = '0.01';
    }
});


revertButton.addEventListener('click', function() {
    const selectedVariants = getSelectedVariants();
    updateRevertModalContent(selectedVariants);
    showRevertModal();
});

revertSubmitButton.addEventListener('click', function() {
    const selectedVariants = getSelectedVariants();
    updateModalContent(selectedVariants);
    hideRevertModal();
});

// Cập nhật nội dung modal "Revert"
function updateRevertModalContent(selectedVariants) {
    revertVariantIdInput.value = selectedVariants.join(',');
}

// Hiển thị modal "Revert"
function showRevertModal() {
    const modal = new bootstrap.Modal(revertModal);
    modal.show();
}

// Ẩn modal "Revert"
function hideRevertModal() {
    const modal = bootstrap.Modal.getInstance(revertModal);
    modal.hide();
}

var disableCheckbox = document.getElementById('collectionCheckbox');
var elementsToDisable = document.querySelectorAll('#normalSearch input');
var selectToEnable = document.getElementById('selectCollection');

disableCheckbox.addEventListener('change', function() {
    if (this.checked) {
        elementsToDisable.forEach(function(element) {
            element.disabled = true;
            element.value = '';
        });
        selectToEnable.disabled = false;
    } else {
        elementsToDisable.forEach(function(element) {
            element.disabled = false;
        });
        selectToEnable.disabled = true;
    }
});
