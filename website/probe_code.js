function getUrlParamer(sParam){
  var sPageURL = window.location.search.substring(1);
  var sURLVariables = sPageURL.split('&');
  for (var i = 0; i < sURLVariables.length; i++){
   
    var sParameterName = sURLVariables[i].split('=');
   
    if (sParameterName[0] == sParam){
        return sParameterName[1];
    }

  }
}


update_page(getUrlParamer('probe_id'));

function other_probes(asn){

  mymap = L.map('mapid_probe').setView([37.9, 25.4], 2);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
      maxZoom: 18,
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      id: 'mapbox.streets'
    }).addTo(mymap);
    
    var probe_icon = new L.Icon({
      iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
      iconSize: [20, 32]
    });


    d3.json("data/asn_map/" + asn + ".json", function(error,probes_list) {

      for (var probe in probes_list){
        L.marker([ probes_list[probe]['latitude'], probes_list[probe]['longitude']] , {icon: probe_icon}).addTo(mymap).bindPopup( '<a href="http://sg-pub.ripe.net/petros/dnsthought/per_probe.html?probe_id=' + probes_list[probe]["prb_id"] + '#">View Probe (id: ' + probes_list[probe]["prb_id"] + ')').openPopup();


      }
    })
}




function per_resolver(ip, mask){
  
  d3.json("data/resolvers/" + ip + "-" + mask + ".json", function(error,resolver) {
    console.log(resolver)
    if(error){
      return
    }
    var qname = "No";
    var ipv4_tcp = "No";
    var ipv6_tcp = "No";
    var ipv6_cap = "No";

    if(resolver["qname_minimization"]){
      qname = "Yes"
    }
    if(resolver["ipv4_tcp"]){
      ipv4_tcp = "Yes"
    }
    if(resolver["ipv6_tcp"]){
      ipv6_tcp = "Yes"
    }
    if(resolver["ipv6_cap"]){
      ipv6_cap = "Yes"
    }

    $('#data_table').append('<tr><td>' + qname + '</td><td>' + ipv4_tcp + '</td><td>' + ipv6_tcp + '</td><td>' + ipv6_cap + '</td></tr>');
    
    probes_per_resolver(resolver["probes"])
  })

}


function probes_per_resolver(probes){

  mymap = L.map('mapid_probe').setView([37.9, 25.4], 2);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
      maxZoom: 18,
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      id: 'mapbox.streets'
    }).addTo(mymap);
    
    var probe_icon = new L.Icon({
      iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
      iconSize: [20, 32]
    });


    for (var probe in probes){
      L.marker([ probes[probe]['latitude'], probes[probe]['longitude']] , {icon: probe_icon}).addTo(mymap).bindPopup( '<a href="http://sg-pub.ripe.net/petros/dnsthought/per_probe.html?probe_id=' + probes[probe]["probe_id"] + '#">View Probe (id: ' + probes[probe]["probe_id"] + ')').openPopup();
    }
}

function update_page(probe_id){
  
  if(probe_id == undefined){  
    $("#title_prbid").append(" | No probe selected")
    $("#dns_status").append("Please select a probe first")
    return
  }else{
    $("#title_prbid").append("| Overview of probe " + probe_id)
    
  }


  d3.json("data/availability_prev/probe" + probe_id + ".json", function(error,data_availability) {

    if(error){
      //$('#main_content_per_probe').html('<div class="row"><div class="col-md-6 col-md-offset-3"><div class="box"><div class="box-body"><h1 style="text-align:center">Sorry, <br></br> No resolvers found. </h1></div<</div></div></row>')
      $("#dns_status").append("Not available")
      
    }

    d3.json("data/capabilities/probes/" + probe_id + ".json", function(error,data_capabilities) {


      if(error){
        return
      }
      $("#asn_source").append(" v4: " + data_capabilities["asn_v4"] +" | v6: " + data_capabilities["asn_v6"] )


      other_probes(data_capabilities["asn_v4"])

      //IF DNS WORKS

      var resolve_works = false

      for(var item in data_capabilities){

        if(data_capabilities[item] == null){
          continue
        }
        if(data_capabilities[item]["resolver_net"] != undefined){
          resolve_works = true
        }
      }

      if(resolve_works){
        $("#dns_status").append('The probe can not connect to a name server <img style="margin-left: 20px; width: 20px;" src="img/no_works.png"/>')
      }else{
        $("#dns_status").append('The probe can connect to a name server <img style="margin-left: 20px; width: 20px;" src="img/works.png"/>')

      }


      if(data_capabilities["ipv4_tcp"]){
        $("#supports_ipv4_tcp").append('The probe resolver is able to perform DNS IPv4 TCP <img style="margin-left: 20px; width: 20px;" src="img/works.png"/>')

      }else{
        $("#supports_ipv4_tcp").append('The probe resolver is not able to perform DNS IPv4 TCP <img style="margin-left: 20px; width: 20px;" src="img/no_works.png"/>')


      }

      if(data_capabilities["ipv6_tcp"]){
        $("#supports_ipv6_tcp").append('The probe resolver is able to perform DNS IPv6 TCP <img style="margin-left: 20px; width: 20px;" src="img/works.png"/>')

      }else{
        $("#supports_ipv6_tcp").append('The probe resolver is not able to perform DNS IPv6 TCP <img style="margin-left: 20px; width: 20px;" src="img/no_works.png"/>')


      }

      if(data_capabilities["ipv6_cap"]){
        $("#ipv6_cap").append('The probe resolver have IPv6 capability <img style="margin-left: 20px; width: 20px;" src="img/works.png"/>')

      }else{
        $("#ipv6_cap").append('The probe resolver does not have IPv6 capability <img style="margin-left: 20px; width: 20px;" src="img/no_works.png"/>')
      }

      if(data_capabilities["qname_minimization"]){ 
        $("#qname_minimization").append('The probe resolver offers QNAME minimization <img style="margin-left: 20px; width: 20px;" src="img/works.png"/>')

      }else{
        $("#qname_minimization").append('The probe resolver does not offer QNAME minimization <img style="margin-left: 20px; width: 20px;" src="img/no_works.png"/>')


      }

      if(data_capabilities["edns0_client_subnet"]){
        $("#edns0_client_subnet").append('The probe resolver delivers edns subnet info  <img style="margin-left: 20px; width: 20px;" src="img/works.png"/>')

      }else{
        $("#edns0_client_subnet").append('The probe resolver does not deliver edns subnet info <img style="margin-left: 20px; width: 20px;" src="img/no_works.png"/>')
      }


      for (var resolver in data_availability){

        $('#data_table').append('<tr><td>' + resolver + '</td><td>' + data_availability[resolver]["1h"][resolver] + '</td><td>' + data_availability[resolver]["6h"][resolver] + '</td></tr>');
      }

      for (var resolver in data_capabilities['resolvers']){

        var resolver_ip;
        var resolver_net;
        var resolver_asn;
        var resolver_edns0;
        var resolver_ipv6_cap;
        var resolver_ipv4_tcp;
        var resolver_ipv6_tcp;
        var resolver_qname;

        if(data_capabilities['resolvers'][resolver]['internal']){
          resolver_ip = data_capabilities['resolvers'][resolver]['internal']
        }else{
          resolver_ip = "~"
        }

        if(data_capabilities['resolvers'][resolver]['resolver_net']){
          resolver_net = '<a href="http://sg-pub.ripe.net/petros/dnsthought/per_resolver.html?resolver_ip=' + data_capabilities['resolvers'][resolver]['resolver_net'].split("/")[0] + '&mask=' + data_capabilities['resolvers'][resolver]['resolver_net'].split("/")[1] + ' ">' + data_capabilities['resolvers'][resolver]['resolver_net'] + '</a>'
        }else{
          resolver_net = "~"
        }

        if(data_capabilities['resolvers'][resolver]['resolver_asn']){
          resolver_asn = data_capabilities['resolvers'][resolver]['resolver_asn']
        }else{
          resolver_asn = "~"
        }

        if(data_capabilities['resolvers'][resolver]['edns0_client_subnet']){
          resolver_edns0 = data_capabilities['resolvers'][resolver]['edns0_client_subnet']
        }else{
          resolver_edns0 = "No"
        }


        if(data_capabilities['resolvers'][resolver]['ipv6_cap']){
          resolver_ipv6_cap = "Yes"
        }else{
          resolver_ipv6_cap = "No"
        }


        if(data_capabilities['resolvers'][resolver]['ipv4_tcp']){
          resolver_ipv4_tcp = "Yes"
        }else{
          resolver_ipv4_tcp = "No"
        }

        if(data_capabilities['resolvers'][resolver]['ipv6_tcp']){
          resolver_ipv6_tcp = "Yes"
        }else{
          resolver_ipv6_tcp = "No"
        }


        if(data_capabilities['resolvers'][resolver]['qname_minimization']){
          resolver_qname = "Yes"
        }else{
          resolver_qname = "No"
        }
        $('#data_table_analytic').append('<tr><td>' + resolver_ip + '</td><td>' + resolver_net + '</td><td>' + resolver_asn + '</td><td>' + resolver_edns0 +  '</td><td>' + resolver_ipv6_cap + '</td><td>' + resolver_ipv4_tcp + '</td><td>' + resolver_ipv6_tcp + '</td><td>' + resolver_qname + '</td></tr>');

      }

    })
  })

}




function plot_map_20(){

    mymap = L.map('mapid_top20').setView([37.9, 25.4], 2);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
      maxZoom: 18,
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      id: 'mapbox.streets'
    }).addTo(mymap);
    
    var common = new L.Icon({
      iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
      iconSize: [14, 20]
    });

    var no_common = new L.Icon({
      iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
      iconSize: [14, 20]
    });




    var legend = L.control({position: 'bottomright'});
    
    legend.onAdd = function (map) {
      var div = L.DomUtil.create('div', 'info legend');

      var tmp = '<div class="box" style="width: 260px;height: 80px;"><p style="margin-top:10px"><b><center>Legend:</center>'

      tmp += '</br><p style="margin-top:-8px; margin-left:10px">Probes using Top 20 resolver <img style="width: 10px;margin-left: 40px;" src="https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png"/> </br>'
      tmp += 'Probes not using Top 20 resolver <img style="width: 10px;margin-left: 19px;" src="https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png"/> </br></b></p><br></br>' + '</div>'
      div.innerHTML = tmp 
      div.firstChild.onmousedown = div.firstChild.ondblclick = L.DomEvent.stopPropagation;
        
        return div;
    };

    legend.addTo(mymap);

    $("#map_of_ripe_atlas_20").append(" | Probes use top 20 common resolvers: " + top_20.length + " / Probes using other resolvers: " + remain_resolvers.length);

    for (var probe in top_20){
      if(top_20[probe]==undefined){
        continue;
      }

      L.marker([ top_20[probe]['latitude'], top_20[probe]['longitude']] , {icon: common}).addTo(mymap)

    
    }
    
    for (var probe in remain_resolvers){
      if(remain_resolvers[probe]==undefined){
        continue
      }
      L.marker([ remain_resolvers[probe]['latitude'], remain_resolvers[probe]['longitude']] , {icon: no_common}).addTo(mymap)
    
    }

}


function qname_map(){
  mymap = L.map('mapid_qname').setView([37.9, 25.4], 2);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {
      maxZoom: 18,
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      id: 'mapbox.streets'
    }).addTo(mymap);
    
    var probe_icon = new L.Icon({
      iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
      iconSize: [20, 32]
    });


    d3.json("data/qname_minimization.json", function(error,probes_list) {

      probes_list = probes_list["probes"]
      for (var probe in probes_list){

        console.log()
        L.marker([ probes_list[probe]['latitude'], probes_list[probe]['longitude']] , {icon: probe_icon}).addTo(mymap).bindPopup( '<a href="http://sg-pub.ripe.net/petros/dnsthought/per_probe.html?probe_id=' + probes_list[probe]["probe_id"] + '#">View Probe (id: ' + probes_list[probe]["probe_id"] + ')').openPopup();


      }
    })


}








