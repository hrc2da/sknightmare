function setupRestaurant(w, h) {
    let padding = 5;
    // define the window
    let svg = d3.select("#window")
        .append("svg")
        .attrs({
            id: "gui_layout",
            width: w,
            height: h,
        });

    // bounding for kitchen
    let dining_width = w * 0.7;
    let dining_height = h * 0.7;
    svg.append('rect').attrs({
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
    let table_box_y = dining_height + padding
    svg.append('rect').attrs({
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
    let marketplace_y = padding
    svg.append('rect').attrs({
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
    d3.json("data/tables.json").then(function (data) {
        let increment = table_box_width / Object.keys(data).length;
        let x = table_box_x + padding * 7;
        let y = table_box_y + padding * 10;
        for (let key in data) {
            let table_data = data[key];
            let table = new Table(table_data['type'], 'Placeholder', table_data['seats'], table_data['size'], table_data['cost'], table_data['daily_upkeep'], x, y);
            let svg_attrs = table.draw();

            let group = svg.append("g").attrs({
                id: 'placeholder_table_' + key
            })

            // add the placeholder icons 
            group.selectAll(".place_holder_table_icon")
                .data(svg_attrs['data'])
                .enter()
                .append(svg_attrs['svg_type'])
                .attrs(svg_attrs['shape_attrs']);

            // add placeholeder text
            group.selectAll(".place_holder_table_text")
                .data(svg_attrs['data'])
                .enter()
                .append("text")
                .text(svg_attrs['text'])
                .attrs(svg_attrs['text_attrs'])

            let new_svg_attrs = {};

            let drag = d3.drag().on('drag', function (d) {
                    d3.select('#candidate_table_').select(svg_attrs['svg_type']).attrs(svg_attrs['shape_drag_attrs']);
                    d3.select('#candidate_table_').select('text').attrs(svg_attrs['text_drag_attrs']);
                }).on('start', function (d) {
                    let new_table_group = svg.append("g").attrs({
                        id: 'candidate_table_'
                    })
                    // deep copy the svg_attrs, find better fix for this.
                    new_svg_attrs = JSON.parse(JSON.stringify(svg_attrs));
                    // create new table_icon
                    new_table_group.selectAll(".new_table_icon")
                        .data(new_svg_attrs['data'])
                        .enter()
                        .append(new_svg_attrs['svg_type'])
                        .attrs(new_svg_attrs['shape_attrs']);

                    // create new table_text
                    new_table_group.selectAll(".new_table_text")
                        .data(new_svg_attrs['data'])
                        .enter()
                        .append("text")
                        .text(new_svg_attrs['text'])
                        .attrs(new_svg_attrs['text_attrs'])
                })
                .on('end', function (d) {
                    let mouseX = d3.mouse(this)[0];
                    let mouseY = d3.mouse(this)[1];

                    if (mouseX < dining_width + padding && mouseX > padding && mouseY > padding && mouseY < dining_height) {
                        let new_table_group = d3.select("#candidate_table_");
                        new_table_group.attrs({
                            id: 'table_' + dining_room.num_tables
                        });
                        dining_room.add_table({
                            'table_svg_attrs': new_svg_attrs,
                            'table_g': new_table_group
                        });
                    } else {
                        d3.select("#candidate_table_").remove();
                    }
                })

            group.call(drag);
            placeholder_tables.push(table);
            x += increment;
        }


    });

    let placeholder_items = [];
    d3.json("data/items.json").then(function (data) {
        let increment = marketplace_height / Object.keys(data).length;
        let x = marketplace_x + padding * 15;
        let y = marketplace_y + padding * 10;
        for (let key in data) {
            let item_data = data[key];
            let item = new Item(item_data['type'], item_data['name'], item_data['size'], item_data['attributes'], x, y);
            let svg_attrs = item.draw();

            let group = svg.append("g").attrs({
                id: 'placeholder_item_' + key
            })

            // add the placeholder icons 
            group.selectAll(".place_holder_item_icon")
                .data(svg_attrs['data'])
                .enter()
                .append(svg_attrs['svg_type'])
                .attrs(svg_attrs['shape_attrs']);

            // add placeholeder text
            group.selectAll(".place_holder_item_text")
                .data(svg_attrs['data'])
                .enter()
                .append("text")
                .text(svg_attrs['text'])
                .attrs(svg_attrs['text_attrs'])

            let new_svg_attrs = {}

            let drag = d3.drag().on('drag', function (d) {
                    d3.select('#candidate_item_').select(svg_attrs['svg_type']).attrs(svg_attrs['shape_drag_attrs']);
                    d3.select('#candidate_item_').select('text').attrs(svg_attrs['text_drag_attrs']);
                }).on('start', function (d) {
                    let new_item_group = svg.append("g").attrs({
                        id: 'candidate_item_'
                    })
                    // deep copy the svg_attrs, find better fix for this.
                    new_svg_attrs = JSON.parse(JSON.stringify(svg_attrs));
                    // create new item_icon
                    new_item_group.selectAll(".new_item_icon")
                        .data(new_svg_attrs['data'])
                        .enter()
                        .append(new_svg_attrs['svg_type'])
                        .attrs(new_svg_attrs['shape_attrs']);

                    // create new item_text
                    new_item_group.selectAll(".new_item_text")
                        .data(new_svg_attrs['data'])
                        .enter()
                        .append("text")
                        .text(new_svg_attrs['text'])
                        .attrs(new_svg_attrs['text_attrs'])
                })
                .on('end', function (d) {
                    let mouseX = d3.mouse(this)[0];
                    let mouseY = d3.mouse(this)[1];

                    if (mouseX < dining_width + padding && mouseX > padding && mouseY > padding && mouseY < dining_height) {
                        let new_item_group = d3.select("#candidate_item_");
                        new_item_group.attrs({
                            id: 'item_' + dining_room.num_items
                        });
                        dining_room.add_item({
                            'item_svg_attrs': new_svg_attrs,
                            'item_g': new_item_group
                        });
                    } else {
                        d3.select("#candidate_item_").remove();
                    }
                })
            group.call(drag);
            placeholder_items.push(item);
            y += increment;
        }
    });

    // setup the viz
    return dining_room;
}

function setupViz(id, w, h) {
    let padding = 10
    let svg = d3.select(id).append('svg').attrs({
        x: 0,
        y: 0,
        width: w,
        height: h,
        id: 'graph_svg'
    });

    let viz = new Viz(svg, 0, 0, w - padding, h);
    viz.initialize();
    return viz;

}