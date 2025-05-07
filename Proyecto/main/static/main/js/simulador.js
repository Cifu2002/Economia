function simularCredito(id) {
    const monto = prompt("Ingrese el monto del crédito:", 5000);
    const plazo = prompt("Ingrese el plazo en meses:", 12);
    const metodo = prompt("Ingrese el método de pago (FRANCES o ALEMAN):", "FRANCES");

    if (!monto || !plazo || !metodo) {
        alert("Simulación cancelada o datos incompletos.");
        return;
    }

    const url = `/admin/simular/${id}/?monto=${monto}&plazo=${plazo}&metodo=${metodo}`;

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error en la simulación.");
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert(
                    `Resultado de la Simulación:\n` +
                    `Cuota: $${data.cuota}\n` +
                    `Seguro: $${data.seguro}\n` +
                    `Cuota Total: $${data.cuota_total}\n` +
                    `Total a Pagar: $${data.total_pagar}`
                );
            }
        })
        .catch(error => {
            console.error(error);
            alert("Ocurrió un error al ejecutar la simulación.");
        });
}
