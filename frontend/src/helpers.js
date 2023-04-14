export function postRequest(url, data, callback){
    let req = new XMLHttpRequest();
    let result = null;
    let formData = new FormData();
    let targetURL = getBackendURL() + url;

    for (const prop in data){
        formData.append(prop,data[prop]);
    }

    req.open("POST", targetURL);
    req.onload = function(){
      if(req.readyState === 4){
        if(req.status === 200 ){
          result = JSON.parse(req.responseText);
          callback(result);
        }
      }
    };
    req.onerror = function() {
      console.error(req.statusText);
    }
    req.send(formData);
}

function getBackendURL(){
  const hostname = window.location.host;
  const protocol = location.protocol;
  // Special case for the production URL, not hosted at a subdomain
  if(hostname == 'medistat.online'){
    return protocol + '//backend-medistat.medistat.online/';
  }
  // "regular" case where we host at a subdomain
  return protocol + '//backend-' + hostname + '/';
}
