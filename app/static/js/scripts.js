$(document).ready(function () {
    // Vérifiez si la table DataTable existe déjà
    if ($.fn.dataTable.isDataTable('#operations-table')) {
        // Si elle existe, détruisez l'instance actuelle avant de la réinitialiser
        $('#operations-table').DataTable().destroy();
    }

   
    // Initialisation de DataTable avec les options
    var table = $('#operations-table').DataTable({
        "order": [[3, "desc"]], // Tri par défaut sur la colonne montant
        "paging": true,
        "pageLength": 10,  // Nombre d'opérations par page
        "lengthMenu": [5, 10, 20],  // Options pour la pagination
        "language": {
            "lengthMenu": "Afficher _MENU_ opérations par page",
            "zeroRecords": "Aucune opération trouvée",
            "info": "Affichage de la page _PAGE_ sur _PAGES_",
            "infoEmpty": "Aucune opération disponible",
            "infoFiltered": "(filtré de _MAX_ opérations au total)",
            "search": "Recherche :",
            "paginate": {
                "first": "Premier",
                "last": "Dernier",
                "next": "Suivant",
                "previous": "Précédent"
            }
        }
    });

    // Recherche via la zone de saisie
    $('#search-button').on('click', function () {
        var searchTerm = $('#search-box').val();
        table.search(searchTerm).draw();
    });

    // Gestion des onglets (Toutes, Dépenses, Recettes)
    $('#all-operations-tab').on('click', function () {
        table.column(0).search('').draw();  // Afficher toutes les opérations
    });

    $('#depenses-tab').on('click', function () {
        table.column(0).search('Dépense').draw();  // Filtrer uniquement les dépenses
    });

    $('#recettes-tab').on('click', function () {
        table.column(0).search('Recette').draw();  // Filtrer uniquement les recettes
    });

    // Gestion du tri ascendant et descendant des colonnes
    $('th').on('click', function () {
        var columnIdx = $(this).index();
        var currentOrder = table.order();

        if (currentOrder[0][0] === columnIdx && currentOrder[0][1] === 'asc') {
            table.order([columnIdx, 'desc']).draw();
        } else {
            table.order([columnIdx, 'asc']).draw();
        }
    });

    // Confirmation de suppression d'une opération
    $('.btn-danger').on('click', function (e) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cette opération ?')) {
            e.preventDefault(); // Empêche le formulaire d'être soumis si l'utilisateur annule
        }
    });
});
