import { getOSMD } from "./getOSMD.js";
import { getZoom} from "./getZoom.js";

const controller = new AbortController();
const state = {
  section: undefined,
  chorale: {
    name: undefined,
    index: undefined
  },
  files: {
    "score": undefined,
    "analysis": undefined,
    "plots": undefined
  }
}

//const btn_select = document.getElementById("select");
const btn_navbar = document.getElementById("navbar");
const btn_home = document.getElementById("home");
const btn_name = document.getElementById("name");
const btn_score = document.getElementById("score");
const btn_download = document.getElementById("download");

const tools = document.getElementById("tools");

const toast = document.getElementById("toast");
const iToast = new bootstrap.Toast(toast);

const spinner = document.getElementById("spinner");
const iSpinner = new bootstrap.Modal(spinner, { keyboard: false });

function getCookie(name) {
  const cookieValue = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return cookieValue ? cookieValue.pop() : "";
}

function showAlert(msg) {
  toast.querySelector(".toast-body").innerText = msg;
  iToast.show();
}

function spinnerShow() {
  iSpinner.show();
}
function spinnerHide() {
  iSpinner.hide();
}

function hideBackground() {
  document.querySelector("body").classList.remove("background");
}

function showBackground() {
    document.querySelector("body").classList.add("background");
}

function showNavbar() {
  btn_navbar.classList.remove("hide");
}

function hideNavbar() {
  btn_navbar.classList.add("hide");
}

function hideTools() {
  if (!tools.classList.contains("d-none")) {
    tools.classList.toggle("d-none"); 
  };
}

function showTools() {
  if (tools.classList.contains("d-none")) {
    tools.classList.toggle("d-none"); 
  };
}

btn_download.addEventListener("click", function() {
  let download = getFileFunction(state.section);
  download();
});

function showSection(id) {
  // Hide all sections
  const sections = document.querySelectorAll("section");
  sections.forEach(section => {
    section.style.display = "none";
    section.style.visibility = "hidden";
  });
  // Show the selected section
  const section = document.getElementById(id);
  if (section) {
    section.style.display = "block";
    section.style.visibility = "visible";
  }
  state.section = id.slice("section-".length);
}

function setName(name, index, file, section) {
  state.section = section;
  state.chorale.index = parseInt(index);
  state.chorale.name = name;
  if (file) {
    state.files[state.section] = file;
  }
  btn_name.innerText = name;
}

btn_home.addEventListener("click", function() {
  setName("");
  hideNavbar();
  hideTools();
  hideBackground();
  showSection("section-home");
});

btn_score.addEventListener("click", function() {
  showBackground();
  showSection("section-score");
});

document.querySelectorAll("#chorals").forEach( item => {
  item.addEventListener("click", async function () {
    const data = await getChorale(this.dataset.index);
    if (data) {
      state.section = "score";
      const name = this.innerText;
      hideTools();
      hideNavbar();
      spinnerShow();
      state.files[state.section] = data.file;
      getOSMD(data.file, "section-score");
      setName(name, this.dataset.index, data.file, "score");
      showBackground();
      showSection("section-score");
      showNavbar();
      showTools();
    } else {
      showAlert("Failed to get choral data");
    }
    spinnerHide();
    });
});

document.querySelectorAll("#analysis-key").forEach( item => {
  item.addEventListener("click", async function () {
    const data = await getAnalysis(this.dataset);
    if (data) {
      state.section = "analysis";
      hideTools();
      hideNavbar();
      spinnerShow();
      state.files[state.section] = data.file;
      getOSMD(data.file, "section-analysis");
      showBackground();
      showSection("section-analysis");
      showNavbar();
      showTools();
    } else {
      showAlert("Failed to get analysis data");
    }
    spinnerHide();
  });
});

document.querySelectorAll("#plots-key").forEach( item => {
  item.addEventListener("click", async function () {
    const data = await getPlot(this.dataset);
    if (data) {
      hideTools();
      hideNavbar();
      spinnerShow();
      hideBackground();
      const div = document.createElement("div");
      div.className = "d-flex flex-row justify-content-center align-items-center";
      div.innerHTML = data.svg[0] + data.svg[1];
      document.getElementById("section-plots").innerHTML = "";
      document.getElementById("section-plots").append(div);
      state.section = "plots";
      state.files[state.section] = data.file;
      showSection("section-plots");
      getZoom("section-plots");
      showNavbar();
      showTools();
    } else {
      showAlert("Failed to get plot data");
    }
    //save current graph/div into json, then check if it exists before creating!?
    spinnerHide();
  });
});

function getFileFunction(type) {
  if (!state.files[state.section]) {
    showAlert("No files found.");
    return
  }
  let getFile;
  switch (type) {
    case "score":
    case "analysis":
      getFile = function () {
        const element = document.createElement("a");
        element.setAttribute("href", state.files[state.section]);
        element.setAttribute("download", "score.musicxml");//filename!
        element.style.display = "none";
        document.body.appendChild(element);
        element.click();
        setTimeout(function() {
          document.body.removeChild(element);
        }, 2000);
      };
      break;
    case "plots":
      getFile = function () {
        const element = document.createElement("a");
        element.setAttribute("href", state.files[state.section]);
        element.setAttribute("download", "plot.png");//filename!
        element.style.display = "none";
        document.body.appendChild(element);
        element.click();
        setTimeout(function() {
          document.body.removeChild(element);
        }, 2000);
      };
      break;
    default:
      getFile = function () {
        showAlert("Undefined type.");
      }
      break;
  }
  return getFile;
}

async function getAnalysis(analysis) {
  if (state.chorale.index < 1) {
    showAlert("Select a Chorale first");
    return
  }
  try {
    const response = await fetch(`/getAnalysis/${analysis.index}/${state.chorale.index}`, {
      signal: controller.signal,
      method: "GET"
    });
    if (!response.ok) {
      const error = await response.json();
      showAlert(error.msg);
      //throw new Error(error.msg);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    showAlert(error);
  }
}

async function getChorale(index) {
  try {
    const response = await fetch("/getChorale", {
      signal: controller.signal,
      method: "POST",
      headers: {"X-CSRFToken": getCookie("csrftoken")},
      body: JSON.stringify({"index":index})
    });
    if (!response.ok) {
      const error = await response.json();
      showAlert(error.msg);
      //throw new Error(error.msg);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    showAlert(error);
  }
}

async function getPlot(plot) {
  // add this plot to the chorale const?
  //this.abortController = controller;
  if (state.chorale.index < 1) {
    showAlert("Select a Chorale first");
    return
  }
  try {
    const response = await fetch(`/getPlots/${plot.index}/${state.chorale.index}`, {
      signal: controller.signal,
      method: "GET"
    });

    if (!response.ok) {
      const error = await response.json();
      showAlert(error.msg);
      //throw new Error(error.msg);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    showAlert(error);
  }
}