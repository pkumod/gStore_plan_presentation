<template>
    <div id="plan-container"></div>
</template>

<script>
import cytoscape from 'cytoscape'
import dagre from 'cytoscape-dagre'
import registerTree from './register-tree'

registerTree(cytoscape)
cytoscape.use(dagre)

export default {
    name: 'PlanTree',
    props: ['plan'],
    data() {
        return {}
    },
    mounted() {
        this.initCy()
        this.$on('renderPlan', () => this.renderPlan())
    },
    methods: {
        initCy() {
            window.cy = cytoscape({
                container: document.getElementById('plan-container'),
                userZoomingEnabled: false,
                userPanningEnabled: false,
                elements: [],
                style: [
                    {
                        selector: 'node',
                        style: {
                            'background-color': '#FF8C05',
                            'label': 'data(label)',
                        },
                    },
                    {
                        selector: 'edge',
                        style: {
                            'width': 3,
                            'line-color': '#ccc',
                            'target-arrow-color': '#ccc',
                            'target-arrow-shape': 'triangle',
                        },
                    },
                    {
                        selector: '.subtree',
                        style: {
                            'shape': 'round-rectangle',
                            'background-color': '#4499EE',
                            'width': 35,
                            'height': 35,
                            'text-valign': 'bottom',
                            'text-halign': 'center',
                        },
                    },
                    {
                        selector: '.BJ',
                        style: {
                            'background-color': '#43A102',
                        },
                    }
                ],
                layout: {
                    name: 'breadthfirst',
                    directed: true,
                    padding: 10,
                },
            })
        },
        renderPlan() {
            let plan = this.plan.replaceAll('BJ', '?BJ')
            let cy = window.cy
            cy.elements().remove()
            cy.reset()
            const variable_number = plan.split(/\?+/).length - 1
            console.log('Variable number: ' + variable_number)
            const node_degree_list = plan.slice(-variable_number).split('')
            console.log('Degree list: ' + node_degree_list)
            const node_list = plan.slice(1, -variable_number).split('?')
            console.log('Node list: ' + node_list)

            let now_node = null
            let tmp_node = null
            let BJ_count = 0
            for (let i = 0; i < node_list.length; i++) {
                let label = node_list[i]
                let BJ_flag = false
                if (label === 'BJ') {
                    BJ_flag = true
                    label = 'BJ' + (BJ_count++)
                }
                switch (node_degree_list[i]) {
                    case '0':
                        addNode(label, {label: label, treepos: 'left'})
                        if (now_node == null)
                            now_node = 'p_' + label
                        else {
                            tmp_node = now_node
                            now_node = 'p_' + label
                        }
                        addNode(now_node, {treepos: 'left', classes: 'subtree'})
                        addEdge(now_node, label)
                        break
                    case '1':
                        addNode(label, {label: label, treepos: 'right'})
                        if (cy.$('#' + now_node).rightChild().length == 1) {
                            cy.$('#' + now_node).data('treepos', 'left')
                            addNode('p_' + now_node, {treepos: 'left', classes: 'subtree'})
                            addEdge('p_' + now_node, now_node)
                            now_node = 'p_' + now_node
                        }
                        addEdge(now_node, label)
                        break
                    case '2':
                        addNode(label, {label: label, treepos: 'left', classes: BJ_flag ? 'subtree BJ' : 'subtree'})
                        cy.$('#' + tmp_node).data('treepos', 'left')
                        cy.$('#' + now_node).data('treepos', 'right')
                        addEdge(label, now_node)
                        addEdge(label, tmp_node)
                        tmp_node = null
                        now_node = label
                        break
                }
            }
            cy.layout({
                name: 'tree',
                siblingDistance: 80,
            }).run()
            cy.elements().lock()
            setTimeout(() => {
                cy.animate({fit: {eles: cy.elements(), padding: 20}})
            }, 500)
        },
    },
}

function addNode(id, options) {
    window.cy.add({
        group: 'nodes',
        data: {
            id: id,
            label: options['label'],
            treepos: options['treepos'],
        },
        classes: options['classes'],
    })
}

function addEdge(source, target) {
    window.cy.add({
        group: 'edges',
        data: {
            source: source,
            target: target,
        },
    })
}

</script>

<style>
#plan-container {
    height: 500px;
    width: 100%;
}
</style>
