document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts
    document.querySelectorAll('.alert-dismissible').forEach(function(el) {
        setTimeout(function() {
            el.style.transition = 'opacity .2s';
            el.style.opacity = '0';
            setTimeout(function() { el.remove(); }, 200);
        }, 4000);
    });

    // Close mobile sidebar on link click
    document.querySelectorAll('.sidebar-link').forEach(function(link) {
        link.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.remove('open');
        });
    });

    // Tab switching
    document.querySelectorAll('.tab-link[data-bs-toggle="tab"]').forEach(function(tab) {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            var target = this.getAttribute('href');
            // Deactivate all tabs
            this.closest('.nav-tabs-custom').querySelectorAll('.tab-link').forEach(function(t) {
                t.classList.remove('active');
            });
            this.classList.add('active');
            // Hide all tab panes
            document.querySelectorAll('.tab-pane').forEach(function(pane) {
                pane.classList.remove('show', 'active');
            });
            // Show target pane
            var targetPane = document.querySelector(target);
            if (targetPane) {
                targetPane.classList.add('show', 'active');
            }
        });
    });

    // Confirm destructive actions
    document.querySelectorAll('[data-confirm]').forEach(function(el) {
        el.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});
