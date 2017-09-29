queue()
    .defer(d3.json, "/cashDash/despesas")
    .await(makeGraphs);

function makeGraphs(error, allrecordsJson) {
	
	//Clean projectsJson data
	//Converting obj to matrix

	var dateFormat = d3.time.format.iso;
	var despesas = allrecordsJson.filter(function (d) {
    	return d["Type"]== "EXPENSE";
	});
	allrecordsJson.forEach(function(d) {
		d["Date"] = dateFormat.parse(d["Date"]);
	});
	
	// we'll need to display month names rather than 0-based index values
	var monthNames = [
			"Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
			"Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
	];

	// we'll need to display day names rather than 0-based index values
	var dayNames = [
			"Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"
	];
	
	//Create a Crossfilter instance
	var ndx = crossfilter(despesas);
	var ndy = crossfilter(allrecordsJson)

	//Define Dimensions
	var dateDim = ndx.dimension(function(d) { return d["Date"]; });
	var monthDim = ndx.dimension(function(d) { return d["Month"]; });
	var yearDim = ndx.dimension(function(d) { return d["Year"]; });
	var typeDim = ndx.dimension(function(d) { return d["Type"]; });
	var subDim = ndx.dimension(function(d) { return d["Sublevel"]; });
	var sub2Dim = ndx.dimension(function(d) { return d["Sublevel2"]; });
	
	//var dateDim = ndx.dimension(function(d) { return d["date_posted"]; });
	//var resourceTypeDim = ndx.dimension(function(d) { return d["resource_type"]; });
	//var povertyLevelDim = ndx.dimension(function(d) { return d["poverty_level"]; });
	//var stateDim = ndx.dimension(function(d) { return d["school_state"]; });
	//var totalDonationsDim = ndx.dimension(function(d) { return d["total_donations"]; });

	//Calculate metrics
	var numByMonth = monthDim.group(); 
	var numByYear = monthDim.group(); 
	var numByType = typeDim.group();
	var numByDate = dateDim.group();
	var numBySub = subDim.group();
	var numBySub2 = sub2Dim.group();

	// Ref: http://stackoverflow.com/questions/23795799/calculating-totals-in-crossfilter-js-using-group-reducecount-and-groupall-re
	var sumByMonth = monthDim.group().reduceSum(function(d) {return d["Value"];});
	var sumByYear = yearDim.group().reduceSum(function(d) {return d["Value"];});
	var sumByType = typeDim.group().reduceSum(function(d) {return d["Value"];});
	var sumBySub = subDim.group().reduceSum(function(d) {return d["Value"];});
	var sumBySub2 = sub2Dim.group().reduceSum(function(d) {return d["Value"];});
	
	//var numProjectsByDate = dateDim.group(); 
	//var numProjectsByResourceType = resourceTypeDim.group();	
	//var numProjectsByPovertyLevel = povertyLevelDim.group();
	//var totalDonationsByState = stateDim.group().reduceSum(function(d) {
	//	return d["Value"];
	//});

	var all = ndx.groupAll();
	var totalDespesas = ndx.groupAll().reduceSum(function(d) {return d["Value"];});
	
	//var totalDonations = ndx.groupAll().reduceSum(function(d) {return d["total_donations"];});
	//var max_state = totalDonationsByState.top(1)[0].value;

	//Define values (to be used in charts)
	var minDate = dateDim.bottom(1)[0]["Date"];
	var maxDate = dateDim.top(1)[0]["Date"];

    //Charts
	//var timeChart = dc.barChart("#time-chart");
	//var resourceTypeChart = dc.rowChart("#resource-type-row-chart");
	//var povertyLevelChart = dc.rowChart("#poverty-level-row-chart");
	//var usChart = dc.geoChoroplethChart("#us-chart");
	//var numberProjectsND = dc.numberDisplay("#number-projects-nd");
	//var totalDonationsND = dc.numberDisplay("#total-donations-nd");
	var totalDespesasND = dc.numberDisplay("#total-despesas-nd");
	var totalDespesasByType = dc.rowChart("#total-despesas-sub-bar")
	var totalDespesasByType2 = dc.rowChart("#total-despesas-sub2-bar")
	var totalDespesasByType3 = dc.rowChart("#total-despesas-sub3-bar")
	var	yearRowChart = dc.rowChart("#chart-ring-years");
	var monthRowChart = dc.rowChart("#chart-row-months");

	// ColormapFirenze https://color.adobe.com
	//chart.ordinalColors(["#468966", "#FFF0A5", "#FFB03B", "#B64926", "#8E2800"]);
	var colorScale = d3.scale.ordinal().range(["#468966", "#FFF0A5", "#FFB03B", "#B64926", "#8E2800"]);

	// Ref: https://dc-js.github.io/dc.js/docs/html/dc.dataCount.html
	totalDespesasND
		.group(totalDespesas)
		.formatNumber(d3.format("3s"))
		.valueAccessor(function(d){return d; });
		
//.colors(d3.scale.ordinal().range(["#468966", "#FFF0A5", "#FFB03B", "#B64926", "#8E2800"]))

	totalDespesasByType
	    .width(300)
        .height(250)
        .dimension(typeDim)
        .group(sumByType)
        .colors(colorScale)
		.xAxis().ticks(4);

        //.colors(colorScale)
        //.on('preRedraw', function(chart) {
    	//	chart.calculateColorDomain();
		//})

	totalDespesasByType2
	    .width(300)
        .height(250)
        .dimension(subDim)
        .group(sumBySub)
        .elasticX(true)
		.xAxis().ticks(4);

	totalDespesasByType3
	    .width(300)
        .height(500)
        .dimension(sub2Dim)
        .group(sumBySub2)
        .elasticX(true)
		.xAxis().ticks(4);

	yearRowChart
		.width(300)
		.height(250)
		.dimension(yearDim)
		.group(sumByYear)
		.colors(d3.scale.category10())
		.label(function(d) {
			return d.key;
		})
		.title(function(d) {
			return d.value;
		})
		.elasticX(true)
		.xAxis().ticks(4);
		
	monthRowChart
		.width(300)
		.height(350)
		.dimension(monthDim)
		.group(sumByMonth)
		.colors(d3.scale.category10())
		.label(function(d) {
			return d.key;
		})
		.title(function(d) {
			return d.value;
		})
		.elasticX(true)
		.xAxis().ticks(2);
/*
	numberProjectsND
		.formatNumber(d3.format("d"))
		.valueAccessor(function(d){return d; })
		.group(all);

	totalDonationsND
		.formatNumber(d3.format("d"))
		.valueAccessor(function(d){return d; })
		.group(totalDonations)
		.formatNumber(d3.format(".3s"));

	timeChart
		.width(600)
		.height(160)
		.margins({top: 10, right: 50, bottom: 30, left: 50})
		.dimension(dateDim)
		.group(numProjectsByDate)
		.transitionDuration(500)
		.x(d3.time.scale().domain([minDate, maxDate]))
		.elasticY(true)
		.xAxisLabel("Year")
		.yAxis().ticks(4);

	resourceTypeChart
        .width(300)
        .height(250)
        .dimension(resourceTypeDim)
        .group(numProjectsByResourceType)
        .xAxis().ticks(4);

	povertyLevelChart
		.width(300)
		.height(250)
        .dimension(povertyLevelDim)
        .group(numProjectsByPovertyLevel)
        .xAxis().ticks(4);


	usChart.width(1000)
		.height(330)
		.dimension(stateDim)
		.group(totalDonationsByState)
		.colors(["#E2F2FF", "#C4E4FF", "#9ED2FF", "#81C5FF", "#6BBAFF", "#51AEFF", "#36A2FF", "#1E96FF", "#0089FF", "#0061B5"])
		.colorDomain([0, max_state])
		.overlayGeoJson(statesJson["features"], "state", function (d) {
			return d.properties.name;
		})
		.projection(d3.geo.albersUsa()
    				.scale(600)
    				.translate([340, 150]))
		.title(function (p) {
			return "State: " + p["key"]
					+ "\n"
					+ "Total Donations: " + Math.round(p["value"]) + " $";
		})

*/
    dc.renderAll();

};