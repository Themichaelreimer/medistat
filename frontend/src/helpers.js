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

  const hostname = process.env.VUE_APP_FRONTEND_HOST;
  const backendHostname = process.env.VUE_APP_BACKEND_HOST;
  const protocol = location.protocol;
  // "regular" case where we host at a subdomain
  if(backendHostname !== undefined){
    console.log(backendHostname);
    return protocol + '//' + backendHostname + '/';
  }
  return protocol + '//backend-' + hostname + '/';
}
