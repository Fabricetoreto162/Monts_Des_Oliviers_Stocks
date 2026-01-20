let deferredPrompt;

// Événement déclenché quand l'app est installable
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    console.log("beforeinstallprompt OK");

    const btn = document.getElementById('installBtn');
    if (btn) btn.style.display = 'block';
});

// Clic sur le bouton
document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('installBtn');

    if (!btn) return;

    btn.addEventListener('click', async () => {
        if (!deferredPrompt) return;

        deferredPrompt.prompt();
        await deferredPrompt.userChoice;

        deferredPrompt = null;
        btn.style.display = 'none';
    });
});
