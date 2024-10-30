// Afficher/masquer le menu déroulant lors du clic sur le bouton userButton
document.getElementById('userButton').addEventListener('click', function(event) {
    event.stopPropagation(); // Empêche le clic de se propager au `window`
    var dropdown = document.getElementById('dropdownMenu');
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
});

// Recherche lorsque l'on appuie sur "Entrée" dans le champ de recherche
document.getElementById("search-box").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Empêche le rechargement de la page
        document.getElementById("search-button").click(); // Simule un clic sur le bouton de recherche
    }
});

// Cacher le menu déroulant lorsqu'on clique en dehors
window.onclick = function(event) {
    var dropdown = document.getElementById('dropdownMenu');
    if (dropdown.style.display === 'block' && !event.target.matches('#userButton')) {
        dropdown.style.display = 'none';
    }
};


$(document).ready(function () {
    // Vérifiez si la table DataTable existe déjà
    if ($.fn.dataTable.isDataTable('#operations-table')) {
        $('#operations-table').DataTable().destroy();
    }

    var table = $('#operations-table').DataTable({
        "order": [[3, "desc"]],
        "paging": true,
        "pageLength": 10,
        "lengthMenu": [5, 10, 20],
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

    // Gestion des onglets
    $('#all-operations-tab').on('click', function () {
        table.column(0).search('').draw();  // Afficher toutes les opérations
    });

    $('#depenses-tab').on('click', function () {
        table.column(1).search('Dépense').draw();  // Filtrer uniquement les dépenses
    });

    $('#recettes-tab').on('click', function () {
        table.column(1).search('Recette').draw();  // Filtrer uniquement les recettes
    });

    $('#releve-bancaire-tab').on('click', function () {
        // Filtrer pour n'afficher que les relevés bancaires
        table.column(0).search('importée').draw();
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
