class MarketPlace {
  constructor(svg,x,y,height,width,padding,num_displayed,dining_room){
    this.svg = svg;
    this.placeholder_items = [];
    this.x = x;
    this.y = y;
    this.height = height;
    this.width = width;
    this.padding = padding;
    this.num_displayed = num_displayed;
    this.item_start = 0;
    this.dining_room = dining_room;
    this.draw.bind(this);
    this.setup_arrows.bind(this);
    return d3.json("data/items.json")
    .then((data)=>{
      console.log(data);
      this.increment = this.height / Object.keys(data).length;
      let x = this.x + this.padding * 15;
      let y = this.y + this.padding * 10;
      for (let key in data){
        let item_data = data[key];
        let item = new Item(
          item_data["type"],
          item_data["name"],
          item_data["size"],
          item_data["attributes"],
          x,
          y
        );
        this.placeholder_items.push(item);
      }
      this.draw(this.item_start,this.num_displayed+this.item_start);
      this.setup_arrows();
    });
  }
  draw = (start,stop) => {
    d3.selectAll(".placeholder_item").remove();
    let increment = (this.height - (2*this.padding*10)) / (stop-start);
    let x = this.x + this.padding * 18;
    let y = this.y + this.padding * 18;
    console.log("hurrro",this.placeholder_items,start,stop,this.placeholder_items.slice(start,stop));
    let items_to_draw = this.placeholder_items.slice(start,stop);
    for (let i in items_to_draw) {
      console.log(items_to_draw[i]);
      let item = items_to_draw[i];
      item.x_original = x;
      item.y_original = y;
      let svg_attrs = item.draw();

      let group = this.svg.append("g").attrs({
        id: "placeholder_item_" + i,
        class: "placeholder_item"
      });

      // add the placeholder icons
      group
        .selectAll(".place_holder_item_icon")
        .data(svg_attrs["data"])
        .enter()
        .append(svg_attrs["svg_type"])
        .attrs(svg_attrs["shape_attrs"]);

      // add placeholeder text
      group
        .selectAll(".place_holder_item_text")
        .data(svg_attrs["data"])
        .enter()
        .append("text")
        .text(svg_attrs["text"])
        .attrs(svg_attrs["text_attrs"]);

      let new_svg_attrs = {};
      let drag = d3
        .drag()
        .on("drag", (d) => {
          d3.select("#candidate_item_")
            .select(svg_attrs["svg_type"])
            .attrs(svg_attrs["shape_drag_attrs"]);
          d3.select("#candidate_item_")
            .select("text")
            .attrs(svg_attrs["text_drag_attrs"]);
        })
        .on("start", (d) => {
          let new_item_group = this.svg.append("g").attrs({
            id: "candidate_item_"
          });
          // deep copy the svg_attrs, find better fix for this.
          new_svg_attrs = JSON.parse(JSON.stringify(svg_attrs));
          // create new item_icon
          new_item_group
            .selectAll(".new_item_icon")
            .data(new_svg_attrs["data"])
            .enter()
            .append(new_svg_attrs["svg_type"])
            .attrs(new_svg_attrs["shape_attrs"]);

          // create new item_text
          new_item_group
            .selectAll(".new_item_text")
            .data(new_svg_attrs["data"])
            .enter()
            .append("text")
            .text(new_svg_attrs["text"])
            .attrs(new_svg_attrs["text_attrs"]);
        })
        .on("end", (d,i,nodes) => {
          let mouseX = d3.mouse(nodes[i])[0];
          let mouseY = d3.mouse(nodes[i])[1];

          if (
            mouseX < this.dining_room.width + this.padding &&
            mouseX > this.padding &&
            mouseY > this.padding &&
            mouseY < this.dining_room.height
          ) {
            let new_item_group = d3.select("#candidate_item_");
            new_item_group.attrs({
              id: "item_" + this.dining_room.num_items
            });
            this.dining_room.add_item({
              item_svg_attrs: new_svg_attrs,
              item_g: new_item_group
            });
          } else {
            d3.select("#candidate_item_").remove();
          }
        });
      group.call(drag);
      y += increment;
    }
  }

  setup_arrows = () => {
    let uparrow = d3.symbol().size(500);
    let downarrow = d3.symbol().size(500);
  
    this.uparrow = this.svg
      .append("path")
      .attr("transform", "translate("+(this.x+this.width/2)+","+(this.y+this.padding*5)+")")
      .attr("class","scroll_button")
      .attr("fill",(d)=>{
        if(this.item_start>0){
          return "gray";
        } 
        else {
          return "lightgray";
        }
      })
      .attr("stroke","darkgray")
      .attr("stroke-width",0)
      .attr("d", uparrow.type(d3.symbolTriangle))
      .on("mouseover", (d,i,nodes)=> {
        if(this.item_start>0){
          d3.select(nodes[i])
          .attr("stroke-width", 4 );
        }
      })
      .on("mouseout", (d,i,nodes)=> {
        d3.select(nodes[i])
        .attr("stroke-width", 0 );
      })
      .on("click", (d,i,nodes) => {
        if(this.item_start > 0){
          this.item_start--;
          this.draw(this.item_start,this.item_start+this.num_displayed)
        }
        this.update_arrows();
      });
    this.downarrow = this.svg
      .append("path")
      .attr("transform", "translate("+(this.x+this.width/2)+","+(this.y+this.height-this.padding*5)+") rotate(180)")
      .attr("class","scroll_button")
      .attr("fill",(d) => {
        if(this.item_start < this.placeholder_items.length-this.num_displayed){
          return "gray";
        } 
        else {
          return "lightgray";
        }
      })
      .attr("stroke","darkgray")
      .attr("stroke-width",0)
      .attr("d", downarrow.type(d3.symbolTriangle))
      .on("mouseover", (d,i,nodes)=> {
        if(this.item_start < this.placeholder_items.length-this.num_displayed){
          d3.select(nodes[i])
          .attr("stroke-width", 4 );
        }
      })
      .on("mouseout", (d,i,nodes)=> {
        d3.select(nodes[i])
        .attr("stroke-width", 0 );
      })
      .on("click", (d,i,nodes) => {
        if(this.item_start < this.placeholder_items.length-this.num_displayed){
          this.item_start++;
          this.draw(this.item_start,this.item_start+this.num_displayed)
        }
        this.update_arrows();
      });   
  }
  update_arrows = () =>{
      this.uparrow
      .attr("fill",(d)=>{
        if(this.item_start>0){
          return "gray";
        } 
        else {
          return "lightgray";
        }
      });
      this.downarrow
      .attr("fill",(d) => {
        if(this.item_start < this.placeholder_items.length-this.num_displayed){
          return "gray";
        } 
        else {
          return "lightgray";
        }
      });
  }

}



function setupRestaurant(w, h) {
  let padding = 5;
  // define the window
  let svg = d3
    .select("#window")
    .append("svg")
    .attrs({
      id: "gui_layout",
      width: w,
      height: h
    });

  // bounding for kitchen
  let dining_width = w * 0.7;
  let dining_height = h * 0.7;
  svg.append("rect").attrs({
    id: "dining_layout",
    x: padding,
    y: padding,
    width: dining_width,
    height: dining_height,
    fill: "none",
    "stroke-width": 2,
    stroke: "black"
  });

  let dining_room = new DiningRoom(dining_width, dining_height, padding);

  // selection pane for tables
  let table_box_width = w * 0.7;
  let table_box_height = h * 0.2;
  let table_box_x = padding;
  let table_box_y = dining_height + padding;
  svg.append("rect").attrs({
    id: "selection_layout",
    x: table_box_x,
    y: table_box_y,
    width: table_box_width,
    height: table_box_height,
    fill: "none",
    "stroke-width": 2,
    stroke: "black"
  });

  //marketplace panel
  let marketplace_width = w * 0.2;
  let marketplace_height = h * 0.9;
  let marketplace_x = dining_width + padding;
  let marketplace_y = padding;
  let marketplace_item_start = 0
  let marketplace_num_displayed = 3
  svg.append("rect").attrs({
    id: "marketplace_layout",
    x: marketplace_x,
    y: marketplace_y,
    width: marketplace_width,
    height: marketplace_height,
    fill: "none",
    "stroke-width": 2,
    stroke: "black"
  });

  // make placeholder tables
  let placeholder_tables = [];
  d3.json("data/tables.json").then(function(data) {
    let increment = table_box_width / Object.keys(data).length;
    let x = table_box_x + padding * 7;
    let y = table_box_y + padding * 10;
    for (let key in data) {
      let table_data = data[key];
      console.log(table_data["noisiness"])
      let table = new Table(
        table_data["type"],
        "Placeholder",
        table_data["seats"],
        table_data["size"],
        table_data["cost"],
        table_data["daily_upkeep"],
        x,
        y,
        table_data["svg_path"],
        table_data["noisiness"],
        table_data["appliances"]
      );
      let svg_attrs = table.draw();

      let group = svg.append("g").attrs({
        id: "placeholder_table_" + key
      });

      // add the placeholder icons
      group
        .selectAll(".place_holder_table_icon")
        .data(svg_attrs["data"])
        .enter()
        .append(svg_attrs["svg_type"])
        .attrs(svg_attrs["shape_attrs"]);

      // add placeholder text
      group
        .selectAll(".place_holder_table_text")
        .data(svg_attrs["data"])
        .enter()
        .append("text")
        .text(svg_attrs["text"])
        .attrs(svg_attrs["text_attrs"]);

      let new_svg_attrs = {};

      let drag = d3
        .drag()
        .on("drag", function(d) {
          d3.select("#candidate_table_")
            .select(svg_attrs["svg_type"])
            .attrs(svg_attrs["shape_drag_attrs"]);
          d3.select("#candidate_table_")
            .select("text")
            .attrs(svg_attrs["text_drag_attrs"]);
        })
        .on("start", function(d) {
          let new_table_group = svg.append("g").attrs({
            id: "candidate_table_"
          });
          // deep copy the svg_attrs, find better fix for this.
          new_svg_attrs = JSON.parse(JSON.stringify(svg_attrs));
          // create new table_icon
          new_table_group
            .selectAll(".new_table_icon")
            .data(new_svg_attrs["data"])
            .enter()
            .append(new_svg_attrs["svg_type"])
            .attrs(new_svg_attrs["shape_attrs"]);

          // create new table_text
          new_table_group
            .selectAll(".new_table_text")
            .data(new_svg_attrs["data"])
            .enter()
            .append("text")
            .text(new_svg_attrs["text"])
            .attrs(new_svg_attrs["text_attrs"]);
        })
        .on("end", function(d) {
          let mouseX = d3.mouse(this)[0];
          let mouseY = d3.mouse(this)[1];

          if (
            mouseX < dining_width + padding &&
            mouseX > padding &&
            mouseY > padding &&
            mouseY < dining_height
          ) {
            let new_table_group = d3.select("#candidate_table_");
            new_table_group.attrs({
              id: "table_" + dining_room.table_id_counter
            });
            dining_room.add_table({
              table_svg_attrs: new_svg_attrs,
              table_g: new_table_group
            });
          } else {
            d3.select("#candidate_table_").remove();
          }
        });

      group.call(drag);
      placeholder_tables.push(table);
      x += increment;
    }
  });
  
  

//let placeholder_items = setup_marketplace(dining_room,marketplace_x,marketplace_y,marketplace_height,marketplace_width,padding,marketplace_item_start,marketplace_num_items_displayed);
 let marketplace = new MarketPlace(svg,marketplace_x,marketplace_y,marketplace_height,marketplace_width,padding,marketplace_num_displayed,dining_room)
  // let placeholder_items = [];
  // svg
  //   .append("text")
  //   .attr("x", marketplace_x + padding * 23) //x)
  //   .attr("y", marketplace_y + marketplace_height - padding * 3) //y + marketplace_height)
  //   .attr("fill", "black")
  //   .text("Staff");
  // d3.json("data/items.json").then(function(data) {
  //   let increment = marketplace_height / Object.keys(data).length;
  //   let x = marketplace_x + padding * 15;
  //   let y = marketplace_y + padding * 10;

  //   for (let key in data) {
  //     let item_data = data[key];
  //     let item = new Item(
  //       item_data["type"],
  //       item_data["name"],
  //       item_data["size"],
  //       item_data["attributes"],
  //       x,
  //       y
  //     );
  //     let svg_attrs = item.draw();

  //     let group = svg.append("g").attrs({
  //       id: "placeholder_item_" + key,
  //       class: "placeholder_item"
  //     });

  //     // add the placeholder icons
  //     group
  //       .selectAll(".place_holder_item_icon")
  //       .data(svg_attrs["data"])
  //       .enter()
  //       .append(svg_attrs["svg_type"])
  //       .attrs(svg_attrs["shape_attrs"]);

  //     // add placeholeder text
  //     group
  //       .selectAll(".place_holder_item_text")
  //       .data(svg_attrs["data"])
  //       .enter()
  //       .append("text")
  //       .text(svg_attrs["text"])
  //       .attrs(svg_attrs["text_attrs"]);

  //     let new_svg_attrs = {};

  //     let drag = d3
  //       .drag()
  //       .on("drag", function(d) {
  //         d3.select("#candidate_item_")
  //           .select(svg_attrs["svg_type"])
  //           .attrs(svg_attrs["shape_drag_attrs"]);
  //         d3.select("#candidate_item_")
  //           .select("text")
  //           .attrs(svg_attrs["text_drag_attrs"]);
  //       })
  //       .on("start", function(d) {
  //         let new_item_group = svg.append("g").attrs({
  //           id: "candidate_item_"
  //         });
  //         // deep copy the svg_attrs, find better fix for this.
  //         new_svg_attrs = JSON.parse(JSON.stringify(svg_attrs));
  //         // create new item_icon
  //         new_item_group
  //           .selectAll(".new_item_icon")
  //           .data(new_svg_attrs["data"])
  //           .enter()
  //           .append(new_svg_attrs["svg_type"])
  //           .attrs(new_svg_attrs["shape_attrs"]);

  //         // create new item_text
  //         new_item_group
  //           .selectAll(".new_item_text")
  //           .data(new_svg_attrs["data"])
  //           .enter()
  //           .append("text")
  //           .text(new_svg_attrs["text"])
  //           .attrs(new_svg_attrs["text_attrs"]);
  //       })
  //       .on("end", function(d) {
  //         let mouseX = d3.mouse(this)[0];
  //         let mouseY = d3.mouse(this)[1];

  //         if (
  //           mouseX < dining_width + padding &&
  //           mouseX > padding &&
  //           mouseY > padding &&
  //           mouseY < dining_height
  //         ) {
  //           let new_item_group = d3.select("#candidate_item_");
  //           new_item_group.attrs({
  //             id: "item_" + dining_room.num_items
  //           });
  //           dining_room.add_item({
  //             item_svg_attrs: new_svg_attrs,
  //             item_g: new_item_group
  //           });
  //         } else {
  //           d3.select("#candidate_item_").remove();
  //         }
  //       });
  //     group.call(drag);
  //     placeholder_items.push(item);
  //     y += increment;
  //   }

      //add "scroll" buttons for marketplace


 

  let x = marketplace_x + marketplace_width - 6 * padding;
  let y = marketplace_y + marketplace_height - 6 * padding;
  let placeholder_waiter = new Staff(x, y);
  let svg_attrs = placeholder_waiter.draw();

  let group = svg.append("g").attrs({
    id: "placeholder_waiter_"
  });

  // add the placeholder icons
  group
    .selectAll(".place_holder_waiter_icon")
    .data(svg_attrs["data"])
    .enter()
    .append(svg_attrs["svg_type"])
    .attrs(svg_attrs["shape_attrs"]);

  let new_svg_attrs = {};

  let drag = d3
    .drag()
    .on("drag", function(d) {
      d3.select("#candidate_waiter_")
        .select(svg_attrs["svg_type"])
        .attrs(svg_attrs["shape_drag_attrs"]);
    })
    .on("start", function(d) {
      let new_item_group = svg.append("g").attrs({
        id: "candidate_waiter_"
      });
      // deep copy the svg_attrs, find better fix for this.
      new_svg_attrs = JSON.parse(JSON.stringify(svg_attrs));
      // create new item_icon
      new_item_group
        .selectAll(".new_waiter_icon")
        .data(new_svg_attrs["data"])
        .enter()
        .append(new_svg_attrs["svg_type"])
        .attrs(new_svg_attrs["shape_attrs"]);
    })
    .on("end", function(d) {
      let mouseX = d3.mouse(this)[0];
      let mouseY = d3.mouse(this)[1];

      if (
        mouseX < dining_width + padding &&
        mouseX > padding &&
        mouseY > padding &&
        mouseY < dining_height
      ) {
        let new_waiter_group = d3.select("#candidate_waiter_");
        new_waiter_group.attrs({
          id: "waiter_" + dining_room.num_waiters
        });
        dining_room.add_staff({
          waiter_svg_attrs: new_svg_attrs,
          waiter_g: new_waiter_group
        });
      } else {
        d3.select("#candidate_waiter_").remove();
      }
    });
  group.call(drag);

  // setup the viz
  return dining_room;
}

function setupViz(id, w, h) {
  let padding = 10;
  let svg = d3
    .select(id)
    .append("svg")
    .attrs({
      x: 0,
      y: 0,
      width: w,
      height: h,
      id: "graph_svg"
    });

  let viz = new Viz(svg, 0, 0, w - padding, h);
  viz.initialize();
  return viz;
}
