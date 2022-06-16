<template>
    <a-layout id="components-layout-demo-top-side">
        <a-layout-header class="header">
            <div class="logo">
                <!--                <img src="./assets/logo.png"/>-->
                gStore-PlanOptimizer
            </div>
            <div class="nav">
                <span>Home</span>
                <span>About</span>
                <span>Paper</span>
                <span>Contact</span>
            </div>
        </a-layout-header>
        <a-layout-content style="padding: 0 50px;">
            <a-layout style="padding: 24px; background: #fff; min-height: calc(100vh - 64px - 69px)">
                <h1 class="title">Query Interface</h1>
                <div class=""></div>
                <!--                <a-textarea-->
                <!--                    style="margin-bottom: 24px"-->
                <!--                    placeholder="Please input your query"-->
                <!--                    v-model="query"-->
                <!--                    :auto-size="{ minRows: 5}"/>-->

                <div ref="queryContainer">
                </div>
                <a-button type="primary" icon="search" class="query-btn" @click="performQuery" :loading="loading">
                    Query Now!
                </a-button>
                <a-divider v-show="show_result">Results</a-divider>
                <a-row>
                    <a-col :span="15">
                        <plan-tree :plan="plan" v-show="show_result" :enable_tip="true" class="result-plan" ref="tree"/>
                        <div v-if="show_result" style="position: absolute; top: 32px;">
                            <br/>
                            <a-button type="primary" @click="openCustomPlanPanel">
                                Commit a Custom Plan
                            </a-button>
                        </div>
                        <!--                        <JSONResult :data="result" :loading="loading" v-show="show_result" class="result-json"/>-->
                    </a-col>
                    <a-col :span="9">
                        <a-table v-show="show_result" :columns="getCol" :data-source="getData" class="result-table">
                            <a slot="name" slot-scope="text">{{ text }}</a>
                        </a-table>
                    </a-col>
                </a-row>
                <!--                <a-row>-->
                <!--                    -->
                <!--                </a-row>-->

                <a-modal v-model="show_custom_plan_panel" title="Custom Plan"
                         :maskClosable="false" :zIndex="10000" width="70vw">
                    <template slot="footer">
                        <a-button key="submit" type="primary" :loading="new_plan_query_loading" @click="query_with_plan">
                            Submit
                        </a-button>
                    </template>
                    <b>Original Plan:</b>
                    <p v-if="plan">{{ plan.split(';').slice(0, 2).join(';') }}</p>
                    <b>Please type your own plan:</b>
                    <a-textarea placeholder="Custom Plan" v-model="new_plan"
                                @change="e=>{this.new_plan_loading = true; throttleInput(e)}"/>

                    <a-row>
                        <a-col :span="11">
                            <plan-tree :plan="plan" v-show="show_custom_plan_panel" :enable_tip="false"
                                       class="result-plan" ref="oldtree"/>
                        </a-col>
                        <a-col :span="2">
                            <div style="height: 700px;">
                                <a-icon type="double-right"
                                        style="margin-top: 340px; font-size: 40px; text-align: center;"/>
                            </div>
                        </a-col>
                        <a-col :span="11">
                            <plan-tree :plan="new_plan + ';;;'" v-show="show_custom_plan_panel" :enable_tip="false"
                                       class="result-plan" ref="newtree" :msg="new_plan_loading ? 'Loading': false"/>
                        </a-col>
                    </a-row>

                </a-modal>
            </a-layout>
        </a-layout-content>
        <a-layout-footer style="text-align: center">
            ©2022 Created by pkumod
        </a-layout-footer>
    </a-layout>
</template>

<script>
import axios from 'axios'
// import JSONResult from './components/result.json'
import PlanTree from './components/planTree'
import Yasqe from '@triply/yasqe'

const throttle = (fn, delay = 2000) => {
    let lastTime = 0, timer = null

    return function () {
        let _this = this
        let _arguments = arguments
        let now = new Date().getTime()
        clearTimeout(timer)
        // 判断上次触发的时间和本次触发的时间差是否小于delay,创建一个timer
        if (now - lastTime < delay) {
            timer = setTimeout(function () {
                lastTime = now
                console.log('执行器触发')
                fn.apply(_this, _arguments)
            }, delay)
        } else {
            // 否则可以直接执行
            lastTime = now
            console.log('直接触发')
            fn.apply(_this, _arguments)
        }
    }
}

export default {
    components: {PlanTree},
    data() {
        return {
            query: '',
            loading: false,
            show_result: false,
            result: {},
            yasqe: null,
            plan: '',
            new_plan: '',
            new_plan_loading: false,
            show_custom_plan_panel: false,
            new_plan_query_loading: false,
            query_url: "http://115.27.161.37:5000/query_opt"
        }
    },
    computed: {
        getCol() {
            if (!('head' in this.result))
                return []
            return this.result.head.vars.map(e => {
                return {
                    title: e,
                    dataIndex: e + '.value',
                    key: e,
                }
            })
        },
        getData() {
            if (!('results' in this.result))
                return []
            return this.result.results.bindings
        },
    },
    mounted() {
        this.initYasqe()
    },
    methods: {
        performQuery() {
            this.loading = true
            axios.post(this.query_url, {
                query: this.yasqe.getValue(),
                plan: ""
            }).then(res => {
                console.log(res)
                this.result = res.data
                this.plan = res.data.Plan
                this.loading = false
                this.show_result = true
                this.$nextTick(() => this.$refs.tree.$emit('renderPlan'))
            })
        },
        initYasqe() {
            console.log(this.$refs.queryContainer)
            this.yasqe = new Yasqe(this.$refs.queryContainer,
                {
                    createShareableLink: false,
                    showQueryButton: false,
                    value: this.query,
                })
        },
        openCustomPlanPanel() {
            this.new_plan = this.plan.split(';').slice(0, 2).join(';')
            this.show_custom_plan_panel = true
            this.$nextTick(() => {
                this.$refs.oldtree.$emit('renderPlan')
                this.$refs.newtree.$emit('renderPlan')
            })
        },
        throttleInput: throttle(function (...args) {
            this.checkNewPlan(...args)
        }, 2000),
        checkNewPlan() {
            this.new_plan_loading = false
            this.$refs.newtree.$emit('renderPlan')
        },
        query_with_plan() {
            console.log('query:', this.yasqe.getValue())
            console.log('plan:', this.plan)
            console.log('new_plan:', this.new_plan)
            this.new_plan_query_loading = true
            axios.post(this.query_url, {
                query: this.yasqe.getValue(),
                plan: this.new_plan
            }).then(res => {
                console.log(res)
                this.result = res.data
                this.plan = res.data.Plan
                this.new_plan_query_loading = false
                this.show_custom_plan_panel = false
                this.show_result = true
                this.$nextTick(() => this.$refs.tree.$emit('renderPlan'))
            })
        },
    },

}
</script>

<style scoped>
@import '~@triply/yasqe/build/yasqe.min.css';
</style>
<style>
.CodeMirror {
    z-index: 0 !important;
}
</style>
<style>
.logo {
    color: #fff;
    font-size: 1.5em;
    font-weight: bold;
    font-style: italic;
    max-width: 300px;
    display: inline-block;
}

.logo img {
    width: auto;
    height: 57px;
    float: left;
}

.title {
    text-align: center;
    font-size: 30px;
    font-weight: bold;
}

.nav {
    float: right;
    color: #aaa;
    font-size: 1.2em;
}

.nav span {
    display: inline-block;
    margin-right: 20px;
    cursor: pointer;
}

.nav span:hover {
    color: #fff;
}

.result-json {
    overflow-x: scroll;
}

.result-table {
    overflow-x: auto;
}
</style>
