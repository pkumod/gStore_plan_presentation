<template>
    <div id="plan-container">
        <div class="show-detail-panel">
            Show Plan Detail:
            <a-switch default-checked @change="switchDetailTip"/>
        </div>
    </div>
</template>

<script>
import cytoscape from 'cytoscape'
import popper from 'cytoscape-popper'
import dagre from 'cytoscape-dagre'
import registerTree from './register-tree'
import tippy, {sticky} from 'tippy.js'
import 'tippy.js/dist/tippy.css'

registerTree(cytoscape)
cytoscape.use(popper)
cytoscape.use(dagre)

export default {
    name: 'PlanTree',
    props: ['plan'],
    data() {
        return {
            tips: {},
            showDetailPlan: true,
        }
    },
    mounted() {
        this.initCy()
        this.$on('renderPlan', () => this.renderPlan())
    },
    methods: {
        switchDetailTip(checked) {
            this.showDetailPlan = checked
            if (checked)
                for (let tip in this.tips)
                    this.tips[tip].show()
            else
                for (let tip in this.tips)
                    this.tips[tip].hide()
        },
        initCy() {
            window.cy = cytoscape({
                container: document.getElementById('plan-container'),
                // userZoomingEnabled: false,
                // userPanningEnabled: false,
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
                    },
                ],
                layout: {
                    name: 'breadthfirst',
                    directed: true,
                    padding: 10,
                },
            })
        },
        renderPlanDetail(plan_true_card_num, plan_est_card_num, plan_exe_time, label) {
            let node = window.cy.nodes().filter(node => node.data('id') === label)
            let ref = node.popperRef()
            let dummyDomEle = document.createElement('div')
            let tip = tippy(dummyDomEle, {
                getReferenceClientRect: ref.getBoundingClientRect,
                trigger: 'manual',
                arrow: false,
                theme: 'light',
                hideOnClick: false,
                sticky: true,
                plugins: [sticky],
                offset: [10, 10],
                placement: node.data('treepos'),
                popperOptions: {
                    modifiers: [
                        {
                            name: 'flip',
                            options: {
                                boundary: this.$el,
                            },
                        },
                        {
                            name: 'preventOverflow',
                            options: {
                                boundary: this.$el,
                            },
                        },
                    ],
                },
                appendTo: this.$el,
                content: () => {
                    let content = document.createElement('div')
                    content.innerHTML = `Plan true card num: ${plan_true_card_num}<br>Plan est card num: ${plan_est_card_num}<br>Plan exe time: ${plan_exe_time} ms`
                    return content
                },
            })
            if (this.showDetailPlan)
                tip.show()
            this.tips[label] = tip
        },
        renderPlan() {
            let plan = this.plan.split(';')
            let cy = window.cy
            cy.elements().remove()
            cy.reset()
            for (let tip in this.tips) {
                this.tips[tip].destroy()
                delete this.tips[tip]
            }
            const variable_number = plan[0].split(/\?+/).length - 1
            console.log('Variable number: ' + variable_number)
            const node_degree_list = plan[1].split('')
            console.log('Degree list: ' + node_degree_list)
            const node_list = plan[0].slice(1, -variable_number).split(/\?+/)
            console.log('Node list: ' + node_list)
            const plan_true_card_num = plan[2].split(',')
            const plan_est_card_num = plan[3].split(',')
            const plan_exe_time = plan[4].split(',')

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
                        if (cy.$('#' + now_node).rightChild().length === 1) {
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
                this.renderPlanDetail(plan_true_card_num[i], plan_est_card_num[i], plan_exe_time[i], i === 0 ? label : cy.$('#' + label).predecessors('node')[0].data('id'))
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
    height: 700px;
    width: 100%;
    position: relative;
    overflow: hidden;
}

.tippy-popper {
    transition: none !important;
}

.show-detail-panel {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 10000;
    padding: 10px;
    background: rgba(0, 0, 0, 0.1);
}
</style>
