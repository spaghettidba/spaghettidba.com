(() => {
  const explorer = document.querySelector(".blog-explorer");
  if (!explorer) return;

  const desktop = window.matchMedia("(min-width: 1200px)");
  const updateLayout = () => {
    explorer.open = desktop.matches;
  };

  updateLayout();
  desktop.addEventListener("change", updateLayout);
})();
