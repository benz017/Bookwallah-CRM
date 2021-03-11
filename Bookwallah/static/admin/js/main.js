$(document).ready(function(){

    $("#f_m").val({{config}});
     $.each({{year}},function(index, value)
        {
            $("#year").append('<option class="year" value=' + value + '>' + value + '</option>');
        });

    title = [false,""];
    var month_list = {{m_list|safe}};
    $("#setf_m").click(function(){
      $s_val= $("#f_m").children("option:selected").val();
      $s_text= $("#f_m").children("option:selected").text();
      $.ajax({
        type:"POST",
        url: "{% url 'main_dashboard' %}",
        data:{fiscalv: $s_val,fiscalt:$s_text},
        success: function(){
        $("#closef_m").click();
        var unique_id = $.gritter.add({
        // (string | mandatory) the heading of the notification
        title: 'Settings have been changed',
        // (string | mandatory) the text inside the notification
        text: 'Please Reload the application to see the changes!!',
        // (string | optional) the image to display on the left
        // (bool | optional) if you want it to fade out on its own or just sit there
        sticky: false,
        // (int | optional) the time you want it to be alive for before fading out
        time: 8000,
        // (string | optional) the class name you want to apply to that specific message
        class_name: 'my-sticky-class'
      });} ,
        });
    });
    groupedbar("schart1",{{nps_label}},{{nps_data|safe}},0);
    groupedbar("schart2",{{cp_label|safe}},{{cp_data|safe}},0);
    groupedbar("schart3",{{sb_label|safe}},{{sb_data|safe}},{{sb_data|list_min}});
    chart({{e_sum}},interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",{{e_sum|length}}),[''],{{ex_type|safe}},title,'pie','exp_chart');
    chart({{c_att_data}},interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",{{c_att_data|length}}),[''],['Attended','Not-Attended'],title,'doughnut','serverstatus02');
    chart({{vol_att_data}},interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",{{vol_att_data|length}}),[''],["Attended","Not-Attended"],title,'doughnut','serverstatus01');
    chart({{ses_p_data}},interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",{{ses_p_data|length}}),[''],["Completed","Upcoming"],title,'doughnut','serverstatus04');
    chart({{k_stat}},interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",{{k_stat|length}}),[''],{{k_stat_label}},title,'doughnut','serverstatus03');
    chart({{m_exp}},"",month_list,[''],title,'line','serverstatus05');
    chart({{months}},"rgba(18,176,226,0.7)",month_list,"No. of Sessions",[true,"Number of Sessions (per month)"],'bar','barchart');
    chart({{k_years}},"rgba(18,176,226,0.7)",[1,2,3,4,5],"No. of Kids",title,'bar','barchart2');


    $("#field").change(function(){

        $(".filter_value").remove();
        $selected= $(this).children("option:selected").text();
        $.ajax({
        type:"POST",
        url: "{% url 'main_dashboard' %}",
        data:{select: $selected},
        success: function(resp){
        $('#value').find('option').remove();
           $value_list = resp.value;
           $("#value").attr('disabled', false);
           $("#value").append('<option class="filter_value" value="0">Select value..</option>');
        $.each($value_list,function(index, value)
        {
            $("#value").append('<option class="filter_value" value=' + (index+1) + '>' + value + '</option>');
        });
       }
      });
        });
      $("#value").change(function(){
        $('.hi').remove();

        $value= $("#value option:selected").text();
        $field= $("#field option:selected").text();
        $year = $("#year option:selected").text();
        //${'#hlight').empty();
        $.ajax({
        type:"POST",
        url: "{% url 'main_dashboard' %}",
        data:{value: $value, field:$field, year:$year},
        success: function(resp){
        $('#image').remove();

          $('#img-container').append('<div id="image" class="col-lg-12 parallax" style="background-image: url(\'/media/'+resp.p_details.image+'\');"></div>');
          $('#pname').text(resp.p_details.project_name);
          $('#contact').text(resp.p_details.contact_number);
          $('#add').text(resp.p_details.address);
          if ((resp.hi !== '') || (resp.is !== '')){
          for (i=0;i<4;i++){
                $('#hlight').append('<li class="hi">'+resp.hi[i]+'</li>');
          }
          }
            $('#kd').show();
            for (i=0;i<resp.m.length;i++){
            $hi = '';
            $is = '';
            if (resp.hi[i]!==undefined){$hi=resp.hi[i];}
            if (resp.is[i]!==undefined){$is=resp.is[i];}
            $('.hvi').append('<tr class="hi" style="height:100%;"><td >'+$hi+'</td><td>'+$is+'</td></tr>');

          }
        //document.getElementById('hlight').innerHTML = '';
        $('#serverstatus01').remove();
        $('#serverstatus04').remove();
        $('#serverstatus02').remove();
        $('#graph1').append('<canvas id="serverstatus01" height="200" width="400" style="margin:0 auto;"></canvas>');
        $('#graph4').append('<canvas id="serverstatus04" height="200" width="300" style="margin:0 auto;"></canvas>');
         $('#graph5').append('<canvas id="serverstatus02" height="200" width="400" style="margin:0 auto;"></canvas>');
        chart(resp.c_att_data,interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",resp.c_att_data.length),[''],["Attended","Not-Attended"],title,'doughnut','serverstatus02');
        chart(resp.vol_att_data,interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",resp.vol_att_data.length),[''],["Attended","Not-Attended"],title,'doughnut','serverstatus01');
        chart(resp.ses_p_data,interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",resp.ses_p_data.length),[''],["Completed","Upcoming"],title,'doughnut','serverstatus04');
        $('#vol_att').text(resp.vol_att+"%");
        $('#c_att').text(resp.c_att+"%");
        $('#ses_p').text(resp.ses_p+"%");
        $('#t_exp').text('$'+resp.t_exp);
        $('#serverstatus05').remove();
        $('#graph6').append('<canvas id="serverstatus05" height="200" width="350" style="margin:0 auto;"></canvas>')
         chart(resp.m_exp,[''],month_list,[''],title,'line','serverstatus05');
         $('#serverstatus03').remove();
         $('#graph3').append('<canvas id="serverstatus03" height="150" width="300" style="margin:0 auto;"></canvas>');
         chart(resp.k_stat,interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",resp.k_stat.length),[''],resp.k_stat_label,title,'doughnut','serverstatus03');
         $('#exp_chart').remove();
         $('#graph7').append('<canvas id="exp_chart" height="200" width="400" style="margin:0 auto;"></canvas>');
         chart(resp.e_sum,interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",resp.e_sum.length),[''],JSON.parse(resp.ex_type),title,'pie','exp_chart');
          $('#male').text(resp.k_m);
          $('#female').text(resp.k_f);
          $('#no_nk').text(resp.no_nk);
          $('#no_k').text(resp.no_k);
          $('#barchart').remove();

         $('#graph').append('<canvas id="barchart" height="500" width="1200" style="margin:0 auto;"></canvas>');
          chart(resp.months,"rgba(18,176,226,0.7)",month_list,"No. of Sessions",[true,"Number of Sessions (per month)"],'bar','barchart');

          $('#barchart2').remove();
          $('#graph2').append('<canvas id="barchart2" height="200" width="350" style="margin:0 auto;margin-top:10px;"></canvas>');
          chart(resp.k_years,"rgba(18,176,226,0.7)",[1,2,3,4,5],"No. of Kids",title,'bar','barchart2');
          $('.desc').remove();

          for (i=0;i<Object.keys(resp.v_list).length;i++){
            var key = Object.keys(resp.v_list)[i];
            $('#v_list').append('<div class="desc"><div class="thumb"><img class="img-circle" src="'+resp.v_list[key][0]+'" width="35px" height="35" align=""></div><div class="details"><p style="margin-bottom:0px;"><a href="#">'+key+'</a><br/><muted>'+resp.v_list[key][1]+'</muted></p></div></div>');
          }


          }
      });

    });

});

    function groupedbar(id,label,dataset,m){
    var ctx = document.getElementById(id).getContext("2d");
    step = dataset.length;
    bg = interpolateColors("rgb(18, 176, 226)", "rgb(52, 73, 94)",step);
    var data = dataset;
    for (i=0;i<step;i++){
    data[i]["backgroundColor"] = bg[i];
    }
var data = {
    labels: label,
    datasets: data
};

var myBarChart = new Chart(ctx, {
    type: 'bar',
    data: data,
    options: {
    plugins: {
      datalabels: {
        color: '#fff',
             }
          },
        barValueSpacing: 20,
        scales: {
        xAxes: [{
            gridLines: {
                color: "rgba(0, 0, 0, 0)",
            },
        }],
        yAxes: [{
            gridLines: {
                color: "rgba(0, 0, 0, 0)",
            },
             ticks: {
                min:m,
                }

        }]
        },

        }
});
    };

    function chart(dat, bgcolor, d_label, label,title, type, id){
            if (type === 'line'){
                        var data = {
                            labels: d_label,
                            datasets: [{
                            data: dat,
                            borderColor:'#12b0e2',
                            }],
                        };
                        var opt = {
                layout: {
                padding: {
                    // Any unspecified dimensions are assumed to be 0
                    top: 25,
                    right:10,
                }
},
                    responsive: false,
                    segmentShowStroke: false,
                     scales: {
        xAxes: [{
            gridLines: {
                color: "rgba(0, 0, 0, 0)",
                display: false,
            }
        }],
        yAxes: [{
            gridLines: {
                color: "rgba(0, 0, 0, 0)",
                display: false,
            },
            ticks: {
                    display: false //this will remove only the label
                }

        }]
        },
                     plugins: {
      datalabels: {
      align: "top",
      anchor: "center",
      offset: 1,
             }
          },
                    legend: {
                    display: false
                    },
                    maintainAspectRatio: true,
                    }
                        }
             else if (type === 'bar'){
                 var data = {
                            labels: d_label,
                            datasets: [{
                            label: label,
                            data: dat,
                            barThickness: 32,
                            backgroundColor:bgcolor,
                            }],
                        };
                        var opt = {
                         layout: {
                padding: {
                    // Any unspecified dimensions are assumed to be 0
                    top: 25,
                }
},
                    scales: {
        xAxes: [{
            gridLines: {
                color: "rgba(0, 0, 0, 0)",
            }
        }],
        yAxes: [{
            gridLines: {
                color: "rgba(0, 0, 0, 0)",
            },

        }]
    },
    events: false,
    tooltips: {
        enabled: false
    },
    hover: {
        animationDuration: 0
    },
    plugins: {
      datalabels: {
        color: '#34495e',
             }
          },

                    responsive: false,
                    legend: {
                    display: false
                    },
                    title :{display: title[0],position:'bottom',text:title[1],fontSize:18,fontFamily:"Arial Rounded MT Bold",padding:15,fontColor:'rgb(52, 73, 94)'},
                    maintainAspectRatio: true,
                    }
             }
             else {
                var data = {
                            datasets: [{
                            data: dat,
                            backgroundColor: bgcolor,
                            borderColor:'#d0eff9',}],
                             labels: label
                        };
                        var opt = {
                    responsive: false,
                    segmentShowStroke: false,
                    legend: {
                    display: true,
                    position: 'top',
                    },
                     plugins: {
                      datalabels: {
                        formatter: (value, ctx) => {
                        let sum = 0;
                        let dataArr = ctx.chart.data.datasets[0].data;
                        dataArr.map(data => {
                            sum += data;
                        });
                        let percentage = (value*100 / sum).toFixed(0)+"%";
                        return percentage;
                        },
                    color: '#fff',
                        }
                    },
                    maintainAspectRatio: true,
                    }
             }

                    ctx = document.getElementById(id).getContext("2d")

                    var myDoughnut = new Chart(ctx,{type:type,data:data,options:opt});
                    };

function interpolateColor(color1, color2, factor) {
    if (arguments.length < 3) {
        factor = 0.5;
    }
    var result = color1.slice();
    for (var i = 0; i < 3; i++) {
        result[i] = Math.round(result[i] + factor * (color2[i] - color1[i]));
    }
    return result;
};
// My function to interpolate between two colors completely, returning an array
function interpolateColors(color1, color2, steps) {
    if (steps === 1){
      return ["rgb(18, 176, 226)"];
    }
    var stepFactor = 1 / (steps - 1),
        interpolatedColorArray = [];

    color1 = color1.match(/\d+/g).map(Number);
    color2 = color2.match(/\d+/g).map(Number);

    for(var i = 0; i < steps; i++) {
        interpolatedColorArray.push("rgb("+interpolateColor(color1, color2, stepFactor * i)+")");
    }

    return interpolatedColorArray;
};