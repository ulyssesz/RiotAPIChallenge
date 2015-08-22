
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) { 
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}

function loadChampions() {
    $.getJSON("data/champions.json", function(data) {
        var championsNode = $("#champions");
        data.map(function(championName) {
            var imageNode = $("<img/>");
            imageNode.addClass("champion_square");
            imageNode.attr("src", "http://ddragon.leagueoflegends.com/cdn/5.7.1/img/champion/{0}.png".format(championName));
            console.log(imageNode);
            championsNode.append(imageNode);
        });
    });
}

function loadItemSet() {
    $.getJSON("data/sample.json", function(data){
        var itemPageNode = $('#item-set');
        itemPageNode.empty();

        data['blocks'].map(function(block) {
            var rowNode = $("<div class='item-row'/>");
            var rowName = $("<div class='row-name'/>");
            rowName.text(block["type"]);

            var itemsNode = $("<div class='items'/>");
            block["items"].map(function(item) {
                var itemNode = $("<img class='item'/>");
                itemNode.attr("src", "http://ddragon.leagueoflegends.com/cdn/5.7.1/img/item/{0}.png".format(item["id"]));
                itemsNode.append(itemNode);
            });

            rowNode.append(rowName);
            rowNode.append(itemsNode);
            itemPageNode.append(rowNode);
        });
    });
}

$(document).ready( function(){
    loadChampions();
    loadItemSet();
})