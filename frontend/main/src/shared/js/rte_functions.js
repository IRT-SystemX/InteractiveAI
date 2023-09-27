

function getCardProcess(){
    swal.showLoading();
          getContextRTE();
          var cards = document.getElementsByClassName("card");
          for (var card = 0; card < cards.length; card++) {
              if (cards[card].classList.contains("light-card-detail-selected")){
              getCard(cards[card].getAttribute("data-urlid"));
              }
            }
            
    }

    function getCard(id_card) {
    if (id_card != null){
      var xmlHttp = new XMLHttpRequest();
      xmlHttp.open("GET", this.host + "/cards/cards/"+id_card,false);
      xmlHttp.setRequestHeader("Authorization","Bearer "+ window.localStorage.token);
      xmlHttp.send(null);
      var response = JSON.parse(xmlHttp.responseText);
      var eventAttributes = response.card.data.metadata;
      console.log(eventAttributes);
      this.jsonEventObject = eventAttributes;
      this.jsonEventObject.event_id = id_card;
      console.log(this.jsonEventObject);
    }
  };

    function getContextRTE(){
      var xhr = new XMLHttpRequest();
      xhr.withCredentials = true;
      xhr.addEventListener("readystatechange", function() {
      if(this.readyState === 4) {
          jsonContextObject = JSON.parse(this.responseText);
          if(document.getElementById("rte_assist_nominal").hidden){
              getRecommandationRTE();
              
          }
      }
      });
      xhr.open("GET", this.host + "/cabcontext/api/v1/contexts");
      xhr.setRequestHeader("Authorization", "Bearer " + window.localStorage.token);
      xhr.send();
      
    }

    function getRecommandationRTE(){
      console.log('getRecommandationRTE')
      document.getElementById('rte_assist').html = "";
      var xhr = new XMLHttpRequest();
      xhr.withCredentials = true;
      xhr.addEventListener("readystatechange", function() {
        if(this.readyState === 4) {
          Swal.hideLoading();
          Swal.close();
          document.body.style.cursor = 'unset';
          console.log(JSON.parse(this.responseText))
           var recosRTE = JSON.parse(this.responseText);
          var bodyHTML = "";
           for (var reco=0;reco<recosRTE.length;reco++){
              var description = recosRTE[reco].description;
              var agent_type = recosRTE[reco].agent_type;
              var title = recosRTE[reco].title;
              var actions = recosRTE[reco].actions;
              sessionStorage.setItem("actions"+"["+ reco + "]", JSON.stringify(actions[0]));
              bodyHTML = "<div><span class='rtePrd'><b onclick ='"+ 'showDesc(' + reco + ')' + " '>" + title + "</b></span><br>" + '<button onclick="applyRecommandation(' +reco+ ')"' + 'class="rteBtn">Appliquer</button><hr>';
              bodyHTML += "<span id='descriptionRTE" + reco + "' hidden>" + description + '</span>';
              document.getElementById('rte_assist').innerHTML += bodyHTML;
              
           }

        }
      });
      xhr.open("POST", this.host + "/cab_recommendation/api/v1/recommendation");
      xhr.setRequestHeader("Content-Type", "application/json");
      xhr.setRequestHeader("Authorization", "Bearer " + window.localStorage.token);
      
      var recommendationBody = 
        { context : this.jsonContextObject[0].data.observation,
          event : this.jsonEventObject
        }
      xhr.send(JSON.stringify(recommendationBody));
      }