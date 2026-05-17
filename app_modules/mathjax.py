from shiny import ui


def mathjax_support():
    return ui.tags.head(
        ui.tags.script(
            """
            window.MathJax = {
                tex: {
                    inlineMath: [["\\\\(", "\\\\)"]],
                    displayMath: [["\\\\[", "\\\\]"]]
                },
                svg: {
                    fontCache: "global"
                }
            };
            """
        ),
        ui.tags.script(
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js",
            async_="async"
        ),
        ui.tags.script(
            """
            window.addEventListener("load", function() {
                let timer = null;

                function renderMath() {
                    if (window.MathJax && window.MathJax.typesetPromise) {
                        window.MathJax.typesetPromise();
                    }
                }

                const observer = new MutationObserver(function() {
                    clearTimeout(timer);
                    timer = setTimeout(renderMath, 200);
                });

                observer.observe(document.body, {
                    childList: true,
                    subtree: true
                });

                setTimeout(renderMath, 500);
            });
            """
        )
    )