var lier = 0;
var controller = 0;

function createSpan(parentId, text, idx) {
    var parent = document.getElementById(parentId);
    var span_obj = document.createElement("span");
    span_obj.setAttribute("id", "line" + idx);
    span_obj.setAttribute("class", "line-text")
    span_obj.onclick = function changeContent() {

        span_obj.style = "font-weight: bold";
        lier = idx;
        controller = 1;
    }
    span_obj.innerHTML = text;
    parent.appendChild(span_obj);
}




// Promise.all to load multiple data
Promise.all(
    [d3.json("data/all_files_triples_sentence.json") //file[0]
        // , d3.json("example_triples_sentence.json"), // file[1] example data
        // d3.json("file_topic.json"), // file[2]
        // d3.json("all_files_triples_sentence.json") // file[]
    ]).then((files) => { // files[n] contains nth file

    // data = files[0]

    // 
    console.log("get", sessionStorage.getItem('file_name'))

    var file_name = sessionStorage.getItem('file_name')
        // console.log(files[2]["3226701 Canada, Inc. v. Qualcomm, Inc., Case No.- 15cv2678-MMA (WVG) (S.D. Cal. Oct. 20, 2017) copy.txt"])
        // console.log("data:", data)
        // "LOUISIANA WHOLESALE v. BAYER AG No. 10-762 (U.S. Dec. 6, 2010).txt" failed

    data = files[0][file_name]


    // Use variable "links" to store the each relation 
    // Use variable "nodes" to store distinct nodes
    var links = [];
    var nodes = {};

    var counter = 1;
    data[0].forEach(element => {
        link1 = {};
        link2 = {};
        link1["source"] = nodes[element[0][0]] || (nodes[element[0][0]] = {
            "name": element[0][0]
        });
        link1["target"] = nodes[element[0][1]] || (nodes[element[0][1]] = {
            "name": element[0][1]
        });
        link1["value"] = 0
        link2["source"] = nodes[element[0][1]] || (nodes[element[0][1]] = {
            "name": element[0][1]
        });
        link2["target"] = nodes[element[0][2]] || (nodes[element[0][2]] = {
            "name": element[0][2]
        });
        link2["value"] = 1
        nodes[element[0][1]]["text"] = element[1]
        nodes[element[0][1]]["line"] = element[2]
        nodes[element[0][0]]["type"] = "object"
        nodes[element[0][1]]["type"] = "relation"
        nodes[element[0][2]]["type"] = "subject"
        counter++
        // link["relation"] = nodes[element[0][1]] || (nodes[element[0][1]] = {"name" : element[0][1]});   // might need to modify how to store the "relation" and "text" data
        // link["relation"] = element[0][1];
        // link["text"] = element[1];
        links.push(link1);
        links.push(link2);
    });

    // show article
    var x = document.createElement("ARTICLE");
    x.setAttribute("id", "myArticle");
    document.getElementById("container2").appendChild(x);

    var heading = document.createElement("H1");
    var txt1 = document.createTextNode("Case Context");
    heading.appendChild(txt1);
    document.getElementById("myArticle").appendChild(heading);

    i = 0;
    data[1].forEach(lineContext => {
        createSpan("myArticle", lineContext, i);
        i++;
    })



    document.getElementById("filter_btn").onclick = filter_object;

    // Cases Dropdown
    cases = []
    d3.map(files[1]).keys().sort().forEach((d, i) => {
        if (d.endsWith("_LDA.txt")) {
            cases.push(d.substring(0, d.length - 8))
        } else {
            cases.push(d.substring(0, d.length - 4))
        }
    })

    var cases_dropdown = d3.select("#cases_dropdown")

    cases_dropdown
        .selectAll("option")
        .data(cases)
        .enter()
        .append("option")
        .attr("value", function(option) {
            return option;
        })
        .text(function(option) {
            return option;
        })

    // listener
    // TODO
    cases_dropdown.on("change", function() {
        selected_case = d3.event.target.value
        svg.selectAll("*").remove()
        create_case_svg(selected_case)

    })

    // Builder click listener
    var submitNewNode = d3.select("#submitNewNodeBtn");
    submitNewNode.on("click", function() {
        addNewNode()
    });

    // Add new node function
    function addNewNode() {
        // event.preventDefault()

        var subVal = document.getElementById("subVal").value
        var relVal = document.getElementById("relVal").value
        var objVal = document.getElementById("objVal").value

        var obj = { "name": objVal, "type": "object" }
        if (controller == 1) {
            var text_line = document.getElementById("line" + lier);

            var rel = { "name": relVal, "type": "relation", "line": lier, "text": text_line.innerHTML };
        } else {
            var rel = { "name": relVal, "type": "relation" };
        }
        var sub = { "name": subVal, "type": "subject" }

        nodes[objVal] = obj
        nodes[relVal] = rel
        nodes[subVal] = sub

        links.push({ "source": obj, "target": rel, "value": 0 })
        links.push({ "source": rel, "target": sub, "value": 1 })

        g.remove()
        g = svg.append("g")
            // g.append("defs").append("marker")    // This section adds in the arrows
            //     .attr("id", "end")
            //     .attr("viewBox", "0 -5 10 10")
            //     .attr("refX", 20)
            //     .attr("refY", -1.5)
            //     .attr("markerWidth", 6)
            //     .attr("markerHeight", 6)
            //     .attr("orient", "auto")
            //     .append("path")
            //     .attr("class", "arrow")
            //     .attr("d", "M0,-5L10,0L0,5");
        if (controller == 1) {
            text_line.style.fontWeight = "normal";
        }
        controller = 0
        draw_from_node_path(nodes, links)
        return false;
    }




    // Configuration data
    var c1 = document.getElementById("container1")
    var width = c1.offsetWidth,
        height = c1.offsetHeight,
        rScale = d3.scaleLinear().range([5, 35]);
    var svg = d3.select("#container1").append("svg")
        .attr("class", "graph-svg-component")
        .attr("width", width)
        .attr("height", height)
        .style("float", "left");
    var g = svg.append("g")
    svg.call(d3.zoom().on("zoom", function() {
        g.attr("transform", d3.event.transform)
    })).on("dblclick.zoom", null);
    var force = d3.forceSimulation()
        .force("link", d3.forceLink().distance(50))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force("x", d3.forceX())
        .force("y", d3.forceY())
        .force("charge", d3.forceManyBody().strength(-400))
        .alphaTarget(1)

    // ###################################################################################################
    function draw_from_node_path(nodes, links) {
        force.nodes(d3.values(nodes))
        force.force("link").links(links)
        force.restart()

        var path = g
            .selectAll("path")
            .data(links)
            .enter()
            .append("path")
            .attr("class", function(d) {
                return "link" + d.value;
            })
            .attr("marker-end", "url(#end)");

        var node = g.selectAll(".node")
            .data(force.nodes())
            .enter().append("g")
            .attr("class", "node")
            .on("dblclick", dblclick)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))

        // add the nodes
        node.append("circle")
            .attr("r", function(d, i) {
                return 10;
            })
            .attr("class", function(d) { // Assign color for "object", "relation", "subject"
                var level;
                if (d["type"] == "object") {
                    level = 1;
                } else if (d["type"] == "subject") {
                    level = 2;
                } else {
                    level = 3;
                }
                return "level" + level;
            });

        // add label
        node.append("text")
            .attr("dx", 12)
            .attr("dy", -10)
            .text(function(d) {
                return d["name"]
            })
        force.on("tick", () => { tick(path, node) })
            // node.exit().remove()
            // force.nodes(force.nodes())  
            // force.force("link").links(links)
            // force.restart()



        force.alphaTarget(0.3).restart();

        function dblclick(d) {
            if (d["type"] == "relation") {
                document.getElementById("line" + d["line"]).setAttribute("style", "background-color: ");
            }
            d3.select(this).select("circle")
                .classed("fixed", false)
            d.fixed = false;
            d.fx = null;
            d.fy = null;
        }

        function dragstarted(d) {
            if (!d3.event.active) force.alphaTarget(0.3).restart();
            if (d["type"] == "relation") {
                document.getElementById("line" + d["line"]).setAttribute("style", "background-color: #FFFF00");
            }
            d3.select(this).select("circle")
                .classed("fixed", true);
            //classed("fixed", true)

            d.fixed = true;
            d.fx = d.x;
            d.fy = d.y;
        };

        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        };

        function dragended(d) {
            if (!d3.event.active) force.alphaTarget(0);
            if (d.fixed == true) {
                d.fx = d.x;
                d.fy = d.y;
            } else {
                d.fx = null;
                d.fy = null;
            }
        };

        // add the straight lines
        function tick(path, node) {
            // let path = g.selectAll("path")
            // let node = g.selectAll(".node")
            path.attr("d", function(d) {
                var dx = d.target.x - d.source.x,
                    dy = d.target.y - d.source.y,
                    dr = Math.sqrt(dx * dx + dy * dy);

                line = "M" + d.source.x + "," + d.source.y +
                    "L" + d.target.x + "," + d.target.y;

                return line;
            });

            node.attr("transform", function(d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
        };

        return_val = [force, node, path];
        return return_val;
    }
    // ###################################################################################################

    var return_val = null;
    return_val = draw_from_node_path(nodes, links)

    console.log(nodes)
    console.log(links)



    // Designed the arrow 
    svg.append("defs").append("marker") // This section adds in the arrows
        .attr("id", "end")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 20)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("path")
        .attr("class", "arrow")
        .attr("d", "M0,-5L10,0L0,5");


    var node_name_list = new Set()

    function filter_object() {
        let object_name = document.getElementById('filter_text').value;
        console.log(object_name)
        draw(object_name)
            // new_nodes and new_links are the remaining nodes and links after filtering
        new_nodes = {}
        new_links = []

        // Filter the node !!!!!!!!!!!!!!!!!

        data[0].forEach(function(d) {
            if (d[0][0] == object_name) {
                node_name_list.add(d[0][0])
                node_name_list.add(d[0][1])
                node_name_list.add(d[0][2])
            }
        })
        var nodes_keys = Object.keys(nodes);
        nodes_keys.forEach(function(d) {
            if (node_name_list.has(d)) {
                new_nodes[d] = nodes[d]
            }
        })

        // Filter the link !!!!!!!!!!!
        links.forEach(function(d) {
            if (node_name_list.has(d["target"]["name"])) {
                new_links.push(d)
            }
        })
        console.log(new_nodes)
            // 
        g.remove()
        g = svg.append("g")
            // g.append("defs").append("marker")    // This section adds in the arrows
            //     .attr("id", "end")
            //     .attr("viewBox", "0 -5 10 10")
            //     .attr("refX", 20)
            //     .attr("refY", -1.5)
            //     .attr("markerWidth", 6)
            //     .attr("markerHeight", 6)
            //     .attr("orient", "auto")
            //     .append("path")
            //     .attr("class", "arrow")
            //     .attr("d", "M0,-5L10,0L0,5");

        draw_from_node_path(new_nodes, new_links)
    }

    function update_object(object_name) {
        // new_nodes and new_links are the remaining nodes and links after filtering
        let new_nodes = {}
        let new_links = []
        let delete_name_list = new Set()
            // Filter the node !!!!!!!!!!!!!!!!!
        data[0].forEach(function(d) {
            if (d[0][0] == object_name) {
                delete_name_list.add(d[0][0])
                delete_name_list.add(d[0][1])
                delete_name_list.add(d[0][2])
            }
        })

        delete_name_list.forEach(function(d) {
            node_name_list.delete(d)
        })
        var nodes_keys = Object.keys(nodes);
        nodes_keys.forEach(function(d) {
            if (node_name_list.has(d)) {
                new_nodes[d] = nodes[d]
            }
        })

        // Filter the link !!!!!!!!!!!
        links.forEach(function(d) {
            if (node_name_list.has(d["target"]["name"])) {
                new_links.push(d)
            }
        })

        // 
        g.remove()
        g = svg.append("g")

        draw_from_node_path(new_nodes, new_links)
    }
    // ###################### add dynamic tag #########################

    function draw(object_name) {
        let parent_div = document.getElementById("filter_tag");
        let button = document.createElement("button");
        button.innerHTML = "&times; " + object_name;
        button.setAttribute("class", "tag-button")
        button.addEventListener("click", function() {
            button.remove()
            node_name_list.delete(object_name)
            update_object(object_name)
        })
        parent_div.appendChild(button)
    }
    // ##################################################################
}).catch((err) => {
    console.log(err);
});