import { getZoom } from "./getZoom.js";

export function getOSMD(file, target) {
    let div = document.createElement("div");
    div.id = `OSMD-${target}`;
    div.classList = "overflow-x-auto overflow-y-hidden";
    let section = document.getElementById(target);
    section.innerHTML = "";
    div.style.height = "80vh";
    section.append(div);
    let zoom = 1;
    const osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay(`OSMD-${target}`);
    osmd.EngravingRules.StaffLineColor = "#AABBAA";
    osmd.setOptions({
      backend: "svg",
      renderSingleHorizontalStaffline: true,
      autoResize: false,
      drawTitle: false,
      drawCredits: false,
      drawSubtitle: false,
      drawComposer: false,
      drawLyricist: false,
      drawMetronomeMarks: false
    });
    osmd
      .load(file)
      .then(
        function() {
          osmd.render();
        }
      )
      .then(
        function() {
          //resize to fit screen hight
          let osmdHeight = document.getElementById(target).querySelector('#osmdCanvasPage1').clientHeight;
          zoom = section.clientHeight / osmdHeight;
          osmd.Zoom = zoom;
          osmd.render();
        }
      ).then(
        function() {   
          getZoom(target);
        });
  }