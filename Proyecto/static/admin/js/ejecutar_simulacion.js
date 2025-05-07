function ejecutarSimulacion(id) {
    // Realiza una solicitud para ejecutar la simulación de forma individual o para todo el queryset
    if (confirm('¿Estás seguro de que deseas ejecutar la simulación para este item?')) {
        // Aquí puedes agregar lógica para enviar la solicitud o redirigir a una vista que ejecute la simulación
        window.location.href = '/admin/app/simulacion/' + id + '/ejecutar_simulacion/';
    }
}
