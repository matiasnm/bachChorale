export function getZoom(target) {
  const svg = document.getElementById(target).querySelector("svg");
  const panZoom = svgPanZoom(svg , {
    zoomEnabled: true,
    controlIconsEnabled: false,
    fit: true,
    center: true,
    dblClickZoomEnabled: true,
    mouseWheelZoomEnabled: true,
    preventMouseEventsDefault: true,
    contain: true,
    zoomScaleSensitivity: 0.2,
    minZoom: 0.5,
    maxZoom: 2,
  })

  document.getElementById("zoom-in").addEventListener("click", function(ev){
    ev.preventDefault()
    panZoom.zoomIn()
  });
  
  document.getElementById("zoom-out").addEventListener("click", function(ev){
    ev.preventDefault()
  
    panZoom.zoomOut()
  });
  
  document.getElementById("zoom-reset").addEventListener("click", function(ev){
    ev.preventDefault()
  
    panZoom.resetZoom()
  });
}

