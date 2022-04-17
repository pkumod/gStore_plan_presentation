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
                    <a-col :span="8">
                        <plan-tree :plan="plan" v-show="show_result" class="result-plan" ref="tree"/>
<!--                        <JSONResult :data="result" :loading="loading" v-show="show_result" class="result-json"/>-->
                    </a-col>
                    <a-col :span="16">
                        <a-table v-show="show_result" :columns="getCol" :data-source="getData" class="result-table">
                            <a slot="name" slot-scope="text">{{ text }}</a>
                        </a-table>
                    </a-col>
                </a-row>
<!--                <a-row>-->
<!--                    -->
<!--                </a-row>-->
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
export default {
    components: {PlanTree},
    data() {
        return {
            query: '',
            loading: false,
            show_result: false,
            result: {},
            yasqe: null,
            plan: ''
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
        }
    },
    mounted(){
        this.initYasqe()
    },
    methods: {
        performQuery() {
            this.loading = true
            axios.post('/query', {
                query: this.yasqe.getValue(),
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
                    value: this.query
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
</style>
