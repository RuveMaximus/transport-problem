const supplyCountElem = document.getElementById('supply');
const demandCountElem = document.getElementById('demand');
const tableContainer = document.getElementById('inputTableContainer');

const buildInputTable = () => {
    tableContainer.innerHTML = '';

    const suppliers = +supplyCountElem.value;
    const consumers = +demandCountElem.value;

    const table = document.createElement('table');

    const headerRow = document.createElement('tr');
    // Пустая ячейка для сдвига потребителей 
    headerRow.innerHTML = '<td></td>';

    for (let i = 0; i < consumers; i++) {
        const headerCell = document.createElement('td');
        headerCell.innerText = `Потребитель ${i+1}`;
        headerRow.appendChild(headerCell);
    }
    const headerCell = document.createElement('td');
    headerCell.innerHTML = '<td>Запасы</td>';
    headerRow.appendChild(headerCell);
    table.appendChild(headerRow);

    for (let i = 0; i < suppliers; i++) {
        const tableRow = document.createElement('tr');
        const headerCell = document.createElement('td');

        headerCell.innerText = `Поставщик ${i+1}`;
        tableRow.appendChild(headerCell);

        for (let j = 0; j < consumers; j++) {
            const tableCell = document.createElement('td');
            const cellInput = document.createElement('input');

            cellInput.type = 'number';
            cellInput.name = 'cost';

            tableCell.appendChild(cellInput);
            tableRow.appendChild(tableCell);
        }
        const supplyCell = document.createElement('td');
        const supplyInput = document.createElement('input');

        supplyInput.name = 'supply';
        supplyInput.type = 'number';

        supplyCell.appendChild(supplyInput);
        tableRow.appendChild(supplyCell);
        table.appendChild(tableRow);
    }
    const demandRow = document.createElement('tr');
    demandRow.innerHTML = '<td>Потребности</td>';
    for (let i = 0; i < consumers; i++) {
        const demandCell = document.createElement('td');
        const demandInput = document.createElement('input');

        demandInput.name = 'demand';
        demandInput.type = 'number';

        demandCell.appendChild(demandInput);
        demandRow.appendChild(demandCell);
    }
    table.appendChild(demandRow);
    tableContainer.appendChild(table);

    document.getElementById('calc-btn').style.display = 'block';
}

const divide = function (data, size) { 
    let result = [];
    for (let i = 0; i < data.length; i+=size) {
        result.push(data.slice(i, i+size));
    }
    return result;
}


const buildResult = function(data) {
    const resultElem = document.getElementById('result');
    resultElem.innerHTML = '';
    const table = document.createElement('table');
    for (const row of data) { 
        const rowElem = document.createElement('tr');
        for (const col of row) {
            const colElem = document.createElement('td');
            colElem.innerText = col;
            rowElem.appendChild(colElem);
        }
        table.appendChild(rowElem);
    }
    resultElem.appendChild(table);
}

document.getElementById('step-1-btn').addEventListener('click', buildInputTable);
document.getElementById('calc-btn').addEventListener('click', async () => {
    const data = {
        costs: [],
        supply: [], 
        demand: [],
        method: ''
    }

    document.querySelectorAll('input[name="cost"]').forEach(elem => {
        data.costs.push(+elem.value);
    });

    document.querySelectorAll('input[name="supply"]').forEach(elem => {
        data.supply.push(+elem.value);
    })

    document.querySelectorAll('input[name="demand"]').forEach(elem => {
        data.demand.push(+elem.value);
    })

    data.method = document.getElementById('method').value;

    data.costs = divide(data.costs, +demandCountElem.value);
    const response = await fetch('http://localhost:8000/solve/', {
        method: 'POST',
        body: JSON.stringify(data), 
        headers: { 'Content-Type': 'application/json' },
    });
    response.json()
        .then(jsonData => { buildResult(jsonData); })
        .catch(err => console.error(err));
});


