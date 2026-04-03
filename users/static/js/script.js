let cargoItems = [{ name: '', weight: '', quantity: '' }];

function showToast(message, isError = true) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification' + (isError ? ' toast-error' : '');
    toast.style.background = isError ? '#d9534f' : '#2c8fbb';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function renderCargo() {
    const container = document.getElementById('cargoContainer');
    if (!container) return;
    
    container.innerHTML = '';
    
    cargoItems.forEach((item, index) => {
        const cargoDiv = document.createElement('div');
        cargoDiv.className = 'cargo-item';
        cargoDiv.innerHTML = `
            <div class="cargo-fields">
                <input type="text" class="cargo-name" name="cargo_name[]" placeholder="Наименование груза *" value="${escapeHtml(item.name)}" data-index="${index}" data-field="name">
                <input type="text" class="cargo-weight" name="cargo_weight[]" placeholder="Вес (кг/тонны)" value="${escapeHtml(item.weight)}" data-index="${index}" data-field="weight">
                <input type="text" class="cargo-qty" name="cargo_quantity[]" placeholder="Кол-во / объем" value="${escapeHtml(item.quantity)}" data-index="${index}" data-field="quantity">
            </div>
            ${cargoItems.length > 1 ? '<button class="remove-cargo" data-index="' + index + '">✖</button>' : ''}
        `;
        container.appendChild(cargoDiv);
    });
    
    document.querySelectorAll('.cargo-name, .cargo-weight, .cargo-qty').forEach(input => {
        input.addEventListener('input', function(e) {
            const idx = parseInt(this.dataset.index);
            const field = this.dataset.field;
            if (cargoItems[idx]) {
                cargoItems[idx][field] = this.value;
            }
        });
    });
    
    document.querySelectorAll('.remove-cargo').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const idx = parseInt(this.dataset.index);
            if (cargoItems.length > 1) {
                cargoItems.splice(idx, 1);
                renderCargo();
            }
        });
    });
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

function addCargo() {
    cargoItems.push({ name: '', weight: '', quantity: '' });
    renderCargo();
}

function validateForm() {
    const required = [];
    
    if (!document.getElementById('waybillNumber').value.trim()) required.push('Номер накладной');
    if (!document.getElementById('waybillDate').value) required.push('Дата составления');
    if (!document.getElementById('shipperName').value.trim()) required.push('Грузоотправитель');
    if (!document.getElementById('shipperAddress').value.trim()) required.push('Адрес отправителя');
    if (!document.getElementById('consigneeName').value.trim()) required.push('Грузополучатель');
    if (!document.getElementById('consigneeAddress').value.trim()) required.push('Адрес получателя');
    if (!document.getElementById('vehicle').value.trim()) required.push('Транспортное средство');
    if (!document.getElementById('loadingDate').value) required.push('Дата погрузки');
    
    const hasValidCargo = cargoItems.some(c => c.name && c.name.trim());
    if (!hasValidCargo) required.push('Хотя бы один груз (наименование)');
    
    return { valid: required.length === 0, missing: required };
}

function syncCargoFromDom() {
    const names = document.querySelectorAll('.cargo-name');
    const weights = document.querySelectorAll('.cargo-weight');
    const quantities = document.querySelectorAll('.cargo-qty');

    cargoItems = Array.from(names).map((input, index) => ({
        name: input.value,
        weight: weights[index] ? weights[index].value : '',
        quantity: quantities[index] ? quantities[index].value : ''
    }));
}

function resetForm() {
    document.getElementById('waybillNumber').value = '';
    document.getElementById('waybillDate').value = '';
    document.getElementById('shipperName').value = '';
    document.getElementById('shipperInn').value = '';
    document.getElementById('shipperAddress').value = '';
    document.getElementById('shipperPhone').value = '';
    document.getElementById('consigneeName').value = '';
    document.getElementById('consigneeInn').value = '';
    document.getElementById('consigneeAddress').value = '';
    document.getElementById('consigneePhone').value = '';
    document.getElementById('vehicle').value = '';
    document.getElementById('driver').value = '';
    document.getElementById('loadingDate').value = '';
    document.getElementById('deliveryDate').value = '';
    document.getElementById('additionalInfo').value = '';
    
    cargoItems = [{ name: '', weight: '', quantity: '' }];
    renderCargo();
    
    showToast('Форма очищена', false);
}

function printWaybill() {
    const validation = validateForm();
    if (!validation.valid) {
        showToast('Заполните обязательные поля: ' + validation.missing.join(', '));
        return;
    }
    
    const data = {
        number: document.getElementById('waybillNumber').value,
        date: document.getElementById('waybillDate').value,
        shipperName: document.getElementById('shipperName').value,
        shipperInn: document.getElementById('shipperInn').value,
        shipperAddress: document.getElementById('shipperAddress').value,
        shipperPhone: document.getElementById('shipperPhone').value,
        consigneeName: document.getElementById('consigneeName').value,
        consigneeInn: document.getElementById('consigneeInn').value,
        consigneeAddress: document.getElementById('consigneeAddress').value,
        consigneePhone: document.getElementById('consigneePhone').value,
        vehicle: document.getElementById('vehicle').value,
        driver: document.getElementById('driver').value,
        loadingDate: document.getElementById('loadingDate').value,
        deliveryDate: document.getElementById('deliveryDate').value,
        additionalInfo: document.getElementById('additionalInfo').value,
        cargo: cargoItems.filter(c => c.name && c.name.trim())
    };
    
    let cargoHtml = '';
    if (data.cargo.length > 0) {
        cargoHtml = '<ul style="margin: 10px 0;">' + data.cargo.map((c, i) => {
            let details = [];
            if (c.weight) details.push(`вес: ${c.weight}`);
            if (c.quantity) details.push(`кол-во: ${c.quantity}`);
            return `<li><strong>${i+1}. ${escapeHtml(c.name)}</strong>${details.length ? ' (' + details.join(', ') + ')' : ''}</li>`;
        }).join('') + '</ul>';
    }
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Транспортная накладная ${data.number}</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Inter', Arial, sans-serif; margin: 2cm; line-height: 1.5; }
                h1 { color: #1f5e7e; border-bottom: 3px solid #2c8fbb; padding-bottom: 10px; margin-bottom: 20px; }
                .row { margin: 12px 0; padding: 8px 0; border-bottom: 1px solid #e0e9f0; display: flex; flex-wrap: wrap; }
                .label { font-weight: bold; width: 200px; color: #2c5a6e; }
                .value { flex: 1; }
                .cargo-block { background: #f9fbfd; padding: 15px; border-radius: 12px; margin: 15px 0; border: 1px solid #e2edf4; }
                .signature { margin-top: 50px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 30px; }
                .sign-line { border-top: 1px solid #000; width: 250px; margin-top: 40px; margin-bottom: 8px; }
                .footer-note { margin-top: 40px; text-align: center; font-size: 10px; color: #8aa6bb; border-top: 1px solid #e2ecf3; padding-top: 15px; }
                @media print {
                    body { margin: 0.5cm; }
                    .sign-line { border-top: 1px solid #000; }
                }
            </style>
        </head>
        <body>
            <h1>🚛 ТРАНСПОРТНАЯ НАКЛАДНАЯ № ${escapeHtml(data.number)}</h1>
            <div class="row"><div class="label">Дата составления:</div><div class="value">${escapeHtml(data.date)}</div></div>
            <div class="row"><div class="label">Грузоотправитель:</div><div class="value"><strong>${escapeHtml(data.shipperName)}</strong><br>${escapeHtml(data.shipperAddress)}${data.shipperPhone ? '<br>тел: ' + escapeHtml(data.shipperPhone) : ''}${data.shipperInn ? '<br>ИНН: ' + escapeHtml(data.shipperInn) : ''}</div></div>
            <div class="row"><div class="label">Грузополучатель:</div><div class="value"><strong>${escapeHtml(data.consigneeName)}</strong><br>${escapeHtml(data.consigneeAddress)}${data.consigneePhone ? '<br>тел: ' + escapeHtml(data.consigneePhone) : ''}${data.consigneeInn ? '<br>ИНН: ' + escapeHtml(data.consigneeInn) : ''}</div></div>
            <div class="row"><div class="label">Транспортное средство:</div><div class="value">${escapeHtml(data.vehicle)}</div></div>
            ${data.driver ? `<div class="row"><div class="label">Водитель:</div><div class="value">${escapeHtml(data.driver)}</div></div>` : ''}
            <div class="row"><div class="label">Дата погрузки:</div><div class="value">${escapeHtml(data.loadingDate)}</div></div>
            ${data.deliveryDate ? `<div class="row"><div class="label">Плановая дата доставки:</div><div class="value">${escapeHtml(data.deliveryDate)}</div></div>` : ''}
            <div class="cargo-block"><div class="label" style="margin-bottom: 10px;">📦 Сведения о грузе:</div>${cargoHtml}</div>
            ${data.additionalInfo ? `<div class="row"><div class="label">Особые отметки:</div><div class="value">${escapeHtml(data.additionalInfo)}</div></div>` : ''}
            <div class="signature">
                <div><div class="sign-line"></div>Подпись грузоотправителя<br><span style="font-size: 12px;">М.П.</span></div>
                <div><div class="sign-line"></div>Подпись грузополучателя<br><span style="font-size: 12px;">М.П.</span></div>
            </div>
            <div class="footer-note">Документ сформирован в системе электронного документооборота<br>${new Date().toLocaleString('ru-RU')}</div>
            <script>
                window.onload = () => {
                    setTimeout(() => {
                        window.print();
                        setTimeout(() => window.close(), 500);
                    }, 200);
                };
            <\/script>
        </body>
        </html>
    `);
    printWindow.document.close();
}

function exportWaybillToCsv() {
    syncCargoFromDom();

    const validation = validateForm();
    if (!validation.valid) {
        showToast('Заполните обязательные поля: ' + validation.missing.join(', '));
        return;
    }

    const rows = [
        ['Поле', 'Значение'],
        ['Номер накладной', document.getElementById('waybillNumber').value],
        ['Дата составления', document.getElementById('waybillDate').value],
        ['Грузоотправитель', document.getElementById('shipperName').value],
        ['ИНН грузоотправителя', document.getElementById('shipperInn').value],
        ['Адрес отправителя', document.getElementById('shipperAddress').value],
        ['Телефон отправителя', document.getElementById('shipperPhone').value],
        ['Грузополучатель', document.getElementById('consigneeName').value],
        ['ИНН грузополучателя', document.getElementById('consigneeInn').value],
        ['Адрес получателя', document.getElementById('consigneeAddress').value],
        ['Телефон получателя', document.getElementById('consigneePhone').value],
        ['Транспортное средство', document.getElementById('vehicle').value],
        ['Водитель', document.getElementById('driver').value],
        ['Дата погрузки', document.getElementById('loadingDate').value],
        ['Плановая дата доставки', document.getElementById('deliveryDate').value],
        ['Дополнительная информация', document.getElementById('additionalInfo').value]
    ];

    rows.push([]);
    rows.push(['Груз', 'Вес', 'Количество']);

    cargoItems
        .filter(item => item.name && item.name.trim())
        .forEach(item => {
            rows.push([item.name, item.weight, item.quantity]);
        });

    const csvContent = rows
        .map(row => row.map(value => `"${String(value || '').replace(/"/g, '""')}"`).join(';'))
        .join('\n');

    const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const number = document.getElementById('waybillNumber').value || 'waybill';
    link.href = URL.createObjectURL(blob);
    link.download = `${number}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);

    showToast('Файл для Excel выгружен', false);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    if (!document.getElementById('waybillDate').value) document.getElementById('waybillDate').value = today;
    if (!document.getElementById('loadingDate').value) document.getElementById('loadingDate').value = today;
    
    renderCargo();
    
    document.getElementById('addCargoBtn').addEventListener('click', addCargo);
    document.getElementById('resetFormBtn').addEventListener('click', resetForm);
    document.getElementById('printWaybillBtn').addEventListener('click', printWaybill);
    document.getElementById('exportExcelBtn').addEventListener('click', exportWaybillToCsv);

    const form = document.getElementById('waybillForm');
    if (form) {
        form.addEventListener('submit', (event) => {
            syncCargoFromDom();
            const validation = validateForm();
            if (!validation.valid) {
                event.preventDefault();
                showToast('Заполните обязательные поля: ' + validation.missing.join(', '));
            }
        });
    }
});
