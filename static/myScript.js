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

// class UserBase(BaseModel):
//     serverId: str
//     characterId: str
//     characterName: str
//     level: int
//     jobId: str
//     jobGrowId: str
//     jobName: str
//     jobGrowName: str
//     fame: int
//     adventureName: str
//     guildName: str
//     deal: int
//     buff: int
    
function sendCharacter() {
      const url = "/saveCharacter";
      const bodyData = {
        "server_id": serverId,
        "character_id": characterId,
        "character_name": characterName,
        "level": level,
        "job_id": jobId,
        "job_grow_id": jobGrowId,
        "job_name": jobName,
        "job_grow_name": jobGrowName,
        "fame": fame,
        "adventure_name": adventureName,
        "guild_name": guildName,
        "deal": 0,
        "buff": 0
      }; // 원하는 body 데이터
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

function sendStatus(){
  const url = "/saveStatus/"+serverId+"/"+characterId;


  fetch(url) // 데이터를 가져올 URL
  .then(response => {
    console.log("response");
    console.log(response);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // JSON 데이터 파싱 (필요에 따라 다른 형식으로 변경 가능)
  })
  .then(data => {
    // 받아온 데이터 활용
    console.log("data");
    console.log(data);
  })
  .catch(error => {
    // 에러 처리 (실패 시)
    console.error('Fetch Error:', error);
  });
}

function sendAvatar(){
  const url = "/saveAvatar/"+serverId+"/"+characterId;

  fetch(url) // 데이터를 가져올 URL
  .then(response => {
    console.log("response");
    console.log(response);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // JSON 데이터 파싱 (필요에 따라 다른 형식으로 변경 가능)
  })
  .then(data => {
    // 받아온 데이터 활용
    console.log("data");
    console.log(data);
  })
  .catch(error => {
    // 에러 처리 (실패 시)
    console.error('Fetch Error:', error);
  });
}

function sendTrait(){
  const url = "/saveTrait/"+serverId+"/"+characterId;

  fetch(url) // 데이터를 가져올 URL
  .then(response => {
    console.log("response");
    console.log(response);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // JSON 데이터 파싱 (필요에 따라 다른 형식으로 변경 가능)
  })
  .then(data => {
    // 받아온 데이터 활용
    console.log("data");
    console.log(data);
  })
  .catch(error => {
    // 에러 처리 (실패 시)
    console.error('Fetch Error:', error);
  });
}

function sendSkill(){
  const url = "/saveSkill/"+serverId+"/"+characterId;

  fetch(url) // 데이터를 가져올 URL
  .then(response => {
    console.log("response");
    console.log(response);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json(); // JSON 데이터 파싱 (필요에 따라 다른 형식으로 변경 가능)
  })
  .then(data => {
    // 받아온 데이터 활용
    console.log("data");
    console.log(data);
  })
  .catch(error => {
    // 에러 처리 (실패 시)
    console.error('Fetch Error:', error);
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





document.addEventListener('DOMContentLoaded', () => {

// 


  fetch(`/getEquipments/${serverId}/${characterId}`)
      .then(response => response.json())
      .then(data => {
          generateEquipmentsTooltip(data);
      })
      .catch(error => {
          console.error('Error fetching equipments data:', error);
      });

  
  fetch('/getAvatar')
      .then(response => response.json())
      .then(data => {
          console.log(data);
          if (data) {
              let avatar = data.avatar;
          }
      }
      )
      .catch(error => {
          console.error('Error fetching avatar data:', error);
      });


});






