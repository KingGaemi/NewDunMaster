// equipmentsJSON is defined in the HTML template

// const characterId = '{{equipmentsJSON.characterId}}';
// const characterName = '{{equipmentsJSON.characterName}}';
// const serverId = '{{serverId}}';
// const adventureName = '{{equipmentsJSON.adventureName}}';
// const jobGrowName = '{{equipmentsJSON.jobGrowName}}';
// const jobName = '{{equipmentsJSON.jobName}}';
// const guildName = '{{equipmentsJSON.guildName}}';
// const fame = '{{fame}}';



function getLastProperty(obj) {
  const keys = Object.keys(obj);
  return obj[keys[keys.length - 1]];
}

function decodeHtmlEntities(html) {
  const txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}

function processJson(json) {
  json = json.slice(1, -1);
  json = json.replace(/&#39;/g, '"');
  json = json.replace(/&#34;/g, '"');
  json = json.replace(/None/g, 'null');
  json = json.replace(/True/g, 'true');
  json = json.replace(/False/g, 'false');
  console.log(json);
  return JSON.parse(json);
}


function sendData() {
  const url = "/users/create";
  const bodyData = {"name": characterName , "charId": characterId,
                    "serverId": serverId, "adventureName": adventureName,
                    "jobGrowName": jobGrowName, "jobName": jobName,
                    "guildName": guildName, "fame": fame}; // 원하는 body 데이터
  console.log(bodyData);
  fetch(url, {
      method: 'POST', // 또는 'GET'
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(bodyData)
  })
  .then(response => {
    console.log(response);
  });
}

function generateEquipmentsTooltip(equipmentsJSON) {
  for (const index in equipmentsJSON['equipment']) {
    const equipment = equipmentsJSON['equipment'][index];
    const targetTooltip = document.getElementById('tooltip_' + (parseInt(index) + 1));
    console.log(equipment);
    console.log(index);
    console.log(targetTooltip);
    if (!targetTooltip) {
      continue; // 툴팁 요소가 없으면 다음 반복으로 넘어감
    }

    let optionString = '';

    if (equipment.customOption) {
      for (const optIndex in equipment.customOption.options) {
        const option = equipment.customOption.options[optIndex];
        optionString = option.explain.replace(/\n/g, '<br>').replace(/&lt;br&gt;/g, '<br>');
        targetTooltip.innerHTML += `<div class="tooltipOption" style="margin-bottom: 15px;">
              <span>${parseInt(optIndex) + 1}옵션<br></span>
              <span>${optionString}<br></span>
            </div>`;
      }
    } else if (equipment.fixedOption) {
      optionString = equipment.fixedOption.explain.replace(/\n/g, '<br>').replace(/&lt;br&gt;/g, '<br>');
      targetTooltip.innerHTML += `<span>고정 옵션</span><br><span>${optionString}</span>`;
    } else if (equipment.asrahanOption) {
      for (const key in equipment.asrahanOption.options) {
        const option = equipment.asrahanOption.options[key];
        optionString = option.explain.replace(/\n/g, '<br>').replace(/&lt;br&gt;/g, '<br>');
        targetTooltip.innerHTML += `<span>${option.name}</span><br><span>${optionString}</span>`;
      }
    } else {
      targetTooltip.innerHTML += '<span>Default</span><span>Default</span>';
    }
    console.log(targetTooltip.innerHTML);
  }
}

const infoContents = document.querySelectorAll('input[name="infoRadio"]');
const contents = document.querySelectorAll('.content');

for (const index in infoContents) {
  const option = infoContents[index];
  if (option.addEventListener) { // Ensure the element is an EventTarget before adding a listener
    option.addEventListener('change', function() {
      contents.forEach(function(content) {
        content.style.display = 'none';
      });
      document.getElementById('content' + (parseInt(index) + 1)).style.display = 'block';
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const characterId = urlParams.get('characterId');
  const serverId = urlParams.get('serverId');


  const url = `/info/${characterId}/${serverId}`;

  fetch(url)
      .then(response => response.json())
      .then(data => {
          generateEquipmentsTooltip(data);
      })
      .catch(error => {
          console.error('Error fetching equipments data:', error);
      });

});






