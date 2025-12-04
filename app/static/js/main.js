// Run on page load
document.addEventListener('DOMContentLoaded', function() {
    autoHideAlerts();
    addFadeInAnimation();
    setupRitualDropdown();
});

// Close success alerts after 5 seconds
function autoHideAlerts() {
    var alerts = document.querySelectorAll('.alert-success');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Fade in cards sequentially
function addFadeInAnimation() {
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card, index) {
        card.style.opacity = '0';
        setTimeout(function() {
            card.style.transition = 'opacity 0.5s ease-in';
            card.style.opacity = '1';
        }, index * 100);
    });
}

// Show ritual description when selected
function setupRitualDropdown() {
    var dropdown = document.getElementById('ritual_id');
    if (!dropdown) return;
    
    dropdown.addEventListener('change', function() {
        var opt = this.options[this.selectedIndex];
        var infoDiv = document.getElementById('ritual_info');
        var descDiv = document.getElementById('ritual_description');
        var srcDiv = document.getElementById('ritual_source');
        
        if (this.value && opt.dataset.description) {
            descDiv.textContent = opt.dataset.description;
            srcDiv.textContent = opt.dataset.source ? 'Source: ' + opt.dataset.source : '';
            infoDiv.style.display = 'block';
        } else {
            infoDiv.style.display = 'none';
        }
    });
}
