<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-brand-block">
        <img src="/icon.svg" alt="ModusOctopus mark" class="nav-mark" />
        <div class="nav-brand-copy">
          <div class="nav-brand">MODUSOCTOPUS</div>
          <div class="nav-subbrand">Real World Simulations</div>
        </div>
      </div>
      <div class="nav-links">
        <a href="https://github.com/666ghj/ModusOctopus" target="_blank" class="github-link">
          View on GitHub <span class="arrow">↗</span>
        </a>
      </div>
    </nav>

    <main class="main-content">
      <section class="hero-section">
        <div class="hero-copy">
          <div class="tag-row">
            <span class="orange-tag">Open source</span>
            <span class="version-text">Local graph by default</span>
            <span class="version-text">Codex and Claude compatible</span>
          </div>

          <h1 class="main-title">
            Run real-world scenarios
            <span class="gradient-text">before the world does</span>
          </h1>

          <p class="hero-desc">
            Upload your documents, run the simulation, and see how the story could spread
            before customers, media, or stakeholders react for real.
          </p>

          <div class="hero-points">
            <span>Open-source and local-first</span>
            <span>Graph from source material</span>
            <span>Agent simulation with report output</span>
          </div>

          <div class="trust-row">
            <div class="trust-card">
              <div class="trust-value">Local by default</div>
              <div class="trust-label">No hosted graph required for a first run</div>
            </div>
            <div class="trust-card">
              <div class="trust-value">CLI-native</div>
              <div class="trust-label">Run with Codex or Claude Code in local mode</div>
            </div>
            <div class="trust-card">
              <div class="trust-value">Inspect everything</div>
              <div class="trust-label">Snapshots, profiles, config, and simulation artifacts stay visible</div>
            </div>
          </div>

        </div>

        <div class="hero-logo-wrap">
<div class="hero-visual-card">
            <img :src="heroLogo" alt="ModusOctopus Logo" class="hero-logo" />
            <div class="visual-caption">
              <div class="visual-title">Built for serious what-if work</div>
              <div class="visual-copy">Structured inputs, graph snapshots, agent prep, simulation runtime, and decision reports in one workflow.</div>
            </div>
          </div>
        </div>

        <div class="demo-callout full-width-demo">
          <div class="demo-callout-copy">
            <div class="demo-eyebrow">Instant demo</div>
            <div class="demo-title">Watch an AI launch turn into a safety panic</div>
            <div class="demo-text">
              Start with a fictional consumer AI companion launch where viral screenshots show confident personal,
              medical, and legal fabrications on day one. The default run is designed to escalate into a wider
              AI safety and regulation backlash.
            </div>
          </div>
          <div class="demo-callout-actions">
            <button class="instant-demo-btn" :disabled="loading" @click="runInstantDemo">
              <span>Run instant demo</span>
              <span class="btn-arrow">→</span>
            </button>
            <button class="instant-demo-btn secondary" :disabled="loading" @click="runQuickProductLaunchDemo">
              <span>Quick product launch demo</span>
              <span class="btn-arrow">→</span>
            </button>
          </div>
          <p class="demo-callout-note">Quick demo delivers the first few simulation turns in under two minutes.</p>
        </div>
      </section>

      <section class="dashboard-section">
        <section class="right-panel wizard-full-width">
          <div class="console-box">
            <div class="wizard-header">
              <div>
                <div v-if="currentWizardStep.id !== 'intro'" class="console-label">{{ currentWizardStep.eyebrow }}</div>
                <div class="wizard-title">{{ currentWizardStep.id === 'intro' ? 'Start here' : currentWizardStep.title }}</div>
              </div>
              <div class="wizard-progress">{{ wizardStepIndex + 1 }} / {{ wizardSteps.length }}</div>
            </div>

            <div v-if="currentWizardStep.id === 'intro'" class="onboarding-step">
              <div class="console-header">
                <span class="console-meta">{{ currentWizardStep.meta }}</span>
              </div>

              <div class="wizard-overview-card intro-guidance">
                <div class="metrics-row">
                  <div class="metric-card">
                    <div class="metric-value">6 steps</div>
                    <div class="metric-label">Clear path from blank screen to runnable simulation</div>
                  </div>
                  <div class="metric-card">
                    <div class="metric-value">2-10 docs</div>
                    <div class="metric-label">Best input range for a fast first run</div>
                  </div>
                </div>

                <div class="steps-container wizard-rail">
                  <div class="steps-header">
                    <span class="diamond-icon">◇</span> Wizard steps
                  </div>

                  <div class="workflow-list">
                    <button
                      v-for="(step, index) in wizardSteps"
                      :key="step.id"
                      type="button"
                      class="workflow-item wizard-step-item"
                      :class="{ active: wizardStepIndex === index }"
                      @click="selectWizardStep(index)"
                    >
                      <span class="step-num">{{ String(index + 1).padStart(2, '0') }}</span>
                      <div class="step-info">
                        <div class="step-title">{{ step.title }}</div>
                        <div class="step-desc">{{ step.meta }}</div>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div v-else-if="currentWizardStep.id === 'scenario'" class="onboarding-step">
              <div class="console-header">
                <span class="console-label">{{ currentWizardStep.eyebrow }}</span>
                <span class="console-meta">{{ currentWizardStep.meta }}</span>
              </div>

              <div class="scenario-grid">
                <button
                  v-for="scenario in scenarios"
                  :key="scenario.id"
                  type="button"
                  class="scenario-card"
                  :class="{ active: selectedScenario === scenario.id }"
                  @click="selectScenario(scenario.id)"
                >
                  <span class="scenario-name">{{ scenario.name }}</span>
                  <span class="scenario-copy">{{ scenario.short }}</span>
                </button>
              </div>

              <div class="guidance-card">
                <div class="guidance-title">{{ currentScenario.name }}</div>
                <p class="guidance-copy">{{ currentScenario.description }}</p>
                <div class="guidance-list">
                  <span v-for="item in currentScenario.examples" :key="item">{{ item }}</span>
                </div>
              </div>
            </div>

            <div v-else-if="currentWizardStep.id === 'graph'" class="onboarding-step">
              <div class="console-header">
                <span class="console-label">{{ currentWizardStep.eyebrow }}</span>
                <span class="console-meta">{{ currentWizardStep.meta }}</span>
              </div>

              <div class="scenario-grid provider-grid">
                <button
                  v-for="backend in graphBackendOptions"
                  :key="backend.id"
                  type="button"
                  class="scenario-card provider-card"
                  :class="{ active: selectedGraphBackend === backend.id }"
                  @click="selectGraphBackend(backend.id)"
                >
                  <span class="scenario-name">{{ backend.name }}</span>
                  <span class="scenario-copy">{{ backend.short }}</span>
                </button>
              </div>

              <div class="guidance-card provider-guidance">
                <div class="guidance-title">{{ currentGraphBackend.name }}</div>
                <p class="guidance-copy">{{ currentGraphBackend.description }}</p>
                <div class="guidance-list">
                  <span>{{ currentGraphBackend.capability }}</span>
                </div>
              </div>
            </div>

            <div v-else-if="currentWizardStep.id === 'provider'" class="onboarding-step">
              <div class="console-header">
                <span class="console-label">{{ currentWizardStep.eyebrow }}</span>
                <span class="console-meta">{{ currentWizardStep.meta }}</span>
              </div>

              <div class="scenario-grid provider-grid">
                <button
                  v-for="provider in providerOptions"
                  :key="provider.id"
                  type="button"
                  class="scenario-card provider-card"
                  :class="{ active: selectedProvider === provider.id }"
                  @click="selectProvider(provider.id)"
                >
                  <span class="scenario-name">{{ provider.name }}</span>
                  <span class="scenario-copy">{{ provider.short }}</span>
                </button>
              </div>

              <div class="guidance-card provider-guidance">
                <div class="guidance-title">{{ currentProvider.name }}</div>
                <p class="guidance-copy">{{ currentProvider.description }}</p>
                <div class="guidance-list">
                  <span>{{ providerSupportsPipeline ? 'Supports full pipeline' : 'Refinement only for this graph backend' }}</span>
                  <span>{{ currentProvider.supportsRefinement ? 'Supports brief refinement' : 'No brief refinement' }}</span>
                </div>
              </div>

              <div v-if="providerTelemetry.length" class="guidance-card provider-guidance provider-telemetry">
                <div class="guidance-title">Billing and usage</div>
                <div class="guidance-list">
                  <span v-for="item in providerTelemetry" :key="item">{{ item }}</span>
                </div>
              </div>

              <div v-if="lastUsageEstimate" class="guidance-card provider-guidance provider-telemetry">
                <div class="guidance-title">Latest token estimate</div>
                <div class="guidance-list">
                  <span>Runtime: {{ lastUsageEstimate.runtime_label || 'Unknown runtime' }}</span>
                  <span>Model: {{ lastUsageEstimate.model_display || lastUsageEstimate.model_name || 'Model not declared' }}</span>
                  <span>Estimated input tokens: {{ formatNumber(lastUsageEstimate.estimated_input_tokens) }}</span>
                  <span>Estimated output tokens: {{ formatNumber(lastUsageEstimate.estimated_output_tokens) }}</span>
                  <span>Estimated total tokens: {{ formatNumber(lastUsageEstimate.estimated_total_tokens) }}</span>
                  <span>Estimated cost: {{ formatUsd(lastUsageEstimate.estimated_cost_usd) }}</span>
                  <span>{{ lastUsageEstimate.cost_note || lastUsageEstimate.note }}</span>
                </div>
              </div>

              <div class="structured-grid provider-fields">
                <label v-if="currentProvider.requiresModel || currentProvider.acceptsModelHint" class="input-group">
                  <span>{{ currentProvider.requiresModel ? 'Model name' : 'Model name (optional)' }}</span>
                  <input v-model="providerForm.model_name" type="text" :disabled="loading || providerLoading" />
                </label>

                <label v-if="currentProvider.requiresBaseUrl" class="input-group">
                  <span>Base URL</span>
                  <input v-model="providerForm.base_url" type="text" :disabled="loading || providerLoading" />
                </label>

                <label v-if="currentProvider.requiresApiKey" class="input-group full-width">
                  <span>API key</span>
                  <input v-model="providerForm.api_key" type="password" :disabled="loading || providerLoading" />
                </label>

                <label v-if="currentProvider.usesExecutable" class="input-group">
                  <span>Executable</span>
                  <input v-model="providerForm.executable" type="text" :disabled="loading || providerLoading" />
                </label>
              </div>

              <div class="provider-actions">
                <button type="button" class="secondary-btn" :disabled="providerLoading || !providerCanValidate" @click="runProviderCheck">
                  {{ providerLoading ? 'Checking...' : 'Check provider' }}
                </button>
                <button type="button" class="secondary-btn" :disabled="refineLoading || !providerCanRefine || !simulationRequirement.trim()" @click="runBriefRefinement">
                  {{ refineLoading ? 'Refining...' : 'Refine brief' }}
                </button>
                <button
                  v-if="refinedBrief"
                  type="button"
                  class="secondary-btn ghost-btn"
                  :disabled="loading || refineLoading"
                  @click="clearRefinedBrief"
                >
                  Reset refined brief
                </button>
              </div>

              <p v-if="providerError" class="error-text">{{ providerError }}</p>
              <p v-if="providerStatusText" class="helper-text">{{ providerStatusText }}</p>
            </div>

            <div v-else-if="currentWizardStep.id === 'documents'" class="onboarding-step">
              <div class="console-header">
                <span class="console-label">{{ currentWizardStep.eyebrow }}</span>
                <span class="console-meta">{{ currentWizardStep.meta }}</span>
              </div>

              <div
                class="upload-zone"
                :class="{ 'drag-over': isDragOver, 'has-files': files.length > 0 }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept=".pdf,.md,.txt"
                  style="display: none"
                  :disabled="loading"
                  @change="handleFileSelect"
                />

                <div v-if="files.length === 0" class="upload-placeholder">
                  <div class="upload-icon">↑</div>
                  <div class="upload-title">Drag files here or click to browse</div>
                  <div class="upload-hint">Good inputs: memo, research notes, feedback, policy draft, statement</div>
                </div>

                <div v-else class="file-list">
                  <div v-for="(file, index) in files" :key="`${file.name}-${index}`" class="file-item">
                    <span class="file-icon">DOC</span>
                    <span class="file-name">{{ file.name }}</span>
                    <button type="button" class="remove-btn" @click.stop="removeFile(index)">×</button>
                  </div>
                </div>
              </div>

              <div class="checklist-card">
                <div class="checklist-title">Before you run</div>
                <ul>
                  <li>Include the actual decision, event, or policy you want to test.</li>
                  <li>Include context about the people or groups likely to react.</li>
                  <li>Use 2-10 documents for a first clean run.</li>
                </ul>
              </div>
            </div>

            <div v-else class="onboarding-step">
              <div class="console-header">
                <span class="console-label">{{ currentWizardStep.eyebrow }}</span>
                <span class="console-meta">{{ currentWizardStep.meta }}</span>
              </div>

              <div class="structured-grid">
                <label class="input-group">
                  <span>Scenario</span>
                  <textarea v-model="brief.scenario" rows="3" :disabled="loading" />
                </label>

                <label class="input-group">
                  <span>Timing</span>
                  <textarea v-model="brief.timing" rows="2" :disabled="loading" />
                </label>

                <label class="input-group">
                  <span>Key stakeholders</span>
                  <textarea v-model="brief.stakeholders" rows="3" :disabled="loading" />
                </label>

                <label class="input-group">
                  <span>Main question</span>
                  <textarea v-model="brief.mainQuestion" rows="3" :disabled="loading" />
                </label>

                <label class="input-group full-width">
                  <span>Success or risk to evaluate</span>
                  <textarea v-model="brief.successRisk" rows="2" :disabled="loading" />
                </label>
              </div>

              <div class="brief-preview">
                <div class="preview-header">
                  <span class="preview-title">Final simulation brief</span>
                  <span class="model-badge">Provider: {{ currentProvider.name }}</span>
                </div>
                <pre>{{ finalSimulationRequirement }}</pre>
                <p v-if="refinedBrief" class="helper-text">Using the refined brief for the next run.</p>
              </div>
            </div>

            <div class="console-section btn-section wizard-actions">
              <button
                class="wizard-nav-btn secondary"
                :disabled="!wizardNavigation.canGoBack || loading"
                @click="goToPreviousWizardStep"
              >
                <span>←</span>
                <span>{{ wizardNavigation.previousLabel }}</span>
              </button>

              <button
                v-if="wizardNavigation.canGoNext"
                class="wizard-nav-btn primary"
                :disabled="!canAdvanceCurrentStep || loading"
                @click="goToNextWizardStep"
              >
                <span>{{ wizardNavigation.nextLabel }}</span>
                <span class="btn-arrow">→</span>
              </button>

              <button
                v-else
                class="start-engine-btn wizard-nav-btn primary"
                :disabled="!canSubmit || loading"
                @click="startSimulation"
              >
                <span>{{ loading ? 'Preparing...' : wizardNavigation.nextLabel }}</span>
                <span class="btn-arrow">→</span>
              </button>

              <p v-if="error" class="error-text">{{ error }}</p>
              <p v-if="helperMessage" class="helper-text">{{ helperMessage }}</p>
            </div>
            </div>
        </section>
      </section>

      <HistoryDatabase />
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import HistoryDatabase from '../components/HistoryDatabase.vue'
import { refineBrief, validateProvider } from '../api/providers'
import { getInstantDemoConfig, getQuickProductLaunchDemoConfig } from '../demo/instantDemo'
import { getOnboardingWizardSteps, getWizardNavigation } from '../onboarding/wizard'
import heroLogo from '../assets/logo/modusoctopus-hero.svg'

const router = useRouter()
const wizardSteps = getOnboardingWizardSteps()

const scenarios = [
  {
    id: 'pricing',
    name: 'Pricing change',
    short: 'Test a price increase, packaging shift, or plan migration.',
    description: 'Best for subscription changes, plan simplification, grandfathering questions, or value communication.',
    defaults: {
      scenario: 'We are planning a pricing or packaging change and want to test likely stakeholder reactions before launch.',
      timing: 'State when the change is announced and when it takes effect.',
      stakeholders: 'Existing customers, prospects, power users, influencers, competitors, media.',
      mainQuestion: 'What reactions are most likely in the first 7-14 days, and what narrative could dominate?',
      successRisk: 'Estimate churn risk, backlash risk, and what communication moves reduce damage.'
    },
    examples: ['Upload pricing memo', 'Upload customer feedback', 'Upload launch draft']
  },
  {
    id: 'launch',
    name: 'Product launch',
    short: 'Stress-test a launch before customers and media see it.',
    description: 'Best for new features, AI launches, roadmap reveals, or launches that need careful messaging.',
    defaults: {
      scenario: 'We are preparing a product or feature launch and want to simulate likely reactions across key audiences.',
      timing: 'State the launch date and any staged rollout context.',
      stakeholders: 'Customers, prospects, internal teams, creators, media, competitors, community voices.',
      mainQuestion: 'How could the launch narrative develop, and what misunderstandings or objections are most likely?',
      successRisk: 'Evaluate launch momentum, trust risk, and where follow-up clarification will matter most.'
    },
    examples: ['Upload launch brief', 'Upload FAQ draft', 'Upload roadmap notes']
  },
  {
    id: 'policy',
    name: 'Policy or org change',
    short: 'Test internal or external reactions to policy and org decisions.',
    description: 'Best for return-to-office policies, org restructures, governance changes, or major internal announcements.',
    defaults: {
      scenario: 'We are planning a policy or organizational change and want to understand how different stakeholder groups may react.',
      timing: 'State the announcement date, rollout date, and any phased adoption details.',
      stakeholders: 'Employees, managers, leadership, external observers, partners, customers.',
      mainQuestion: 'Which groups are likely to resist, amplify, or reshape the narrative after the change is announced?',
      successRisk: 'Estimate morale risk, reputational spillover, and operational consequences.'
    },
    examples: ['Upload policy draft', 'Upload org notes', 'Upload survey findings']
  },
  {
    id: 'crisis',
    name: 'Reputation or crisis',
    short: 'Model narrative escalation, stakeholder response, and second-order effects.',
    description: 'Best for sensitive announcements, public incidents, PR risk, or reputation recovery planning.',
    defaults: {
      scenario: 'We need to simulate a sensitive or adversarial public scenario before it unfolds further.',
      timing: 'State what has already happened and the next likely public moment.',
      stakeholders: 'Media, customers, affected groups, critics, allies, employees, regulators.',
      mainQuestion: 'How could the public narrative evolve, and where are the key escalation points?',
      successRisk: 'Evaluate backlash, trust erosion, and what response strategy changes the trajectory.'
    },
    examples: ['Upload statement draft', 'Upload timeline notes', 'Upload external coverage']
  },
  {
    id: 'custom',
    name: 'Custom',
    short: 'Use your own structure if none of the templates fit well.',
    description: 'Best when your scenario is unusual or you already know exactly how you want to frame it.',
    defaults: {
      scenario: '',
      timing: '',
      stakeholders: '',
      mainQuestion: '',
      successRisk: ''
    },
    examples: ['Bring your own framing', 'Paste your own structured brief', 'Use optional agent refinement']
  }
]

const providerOptions = [
  {
    id: 'openai_compatible',
    name: 'OpenAI-compatible API',
    short: 'Use any OpenAI-style endpoint with your own API key.',
    description: 'Best when you want to use OpenRouter, vLLM, or another OpenAI-compatible deployment for both refinement and the full pipeline.',
    requiresApiKey: true,
    requiresBaseUrl: true,
    requiresModel: true,
    usesExecutable: false,
    supportsPipeline: true,
    supportsRefinement: true
  },
  {
    id: 'openai',
    name: 'OpenAI API',
    short: 'Use OpenAI directly for refinement and the full ModusOctopus pipeline.',
    description: 'Best when you want one provider for ontology generation, simulation prep, reports, and brief refinement.',
    requiresApiKey: true,
    requiresBaseUrl: false,
    requiresModel: true,
    usesExecutable: false,
    supportsPipeline: true,
    supportsRefinement: true
  },
  {
    id: 'anthropic',
    name: 'Anthropic API',
    short: 'Use Claude models via Anthropic API for the full pipeline.',
    description: 'Best when you want Claude to handle brief refinement and the simulation pipeline through an API key.',
    requiresApiKey: true,
    requiresBaseUrl: false,
    requiresModel: true,
    usesExecutable: false,
    supportsPipeline: true,
    supportsRefinement: true
  },
  {
    id: 'codex_cli',
    name: 'Codex CLI',
    short: 'Use your local Codex installation for the local graph pipeline.',
    description: 'Best when you want a local-first run: Codex handles refinement and local graph generation without a separate LLM API key.',
    requiresApiKey: false,
    requiresBaseUrl: false,
    requiresModel: false,
    acceptsModelHint: true,
    usesExecutable: true,
    supportsPipeline: true,
    supportsRefinement: true
  },
  {
    id: 'claude_code_cli',
    name: 'Claude Code CLI',
    short: 'Use your local Claude Code installation for the local graph pipeline.',
    description: 'Best when you want Claude Code to drive refinement and the local graph pipeline without another model API.',
    requiresApiKey: false,
    requiresBaseUrl: false,
    requiresModel: false,
    acceptsModelHint: true,
    usesExecutable: true,
    supportsPipeline: true,
    supportsRefinement: true
  }
]

const graphBackendOptions = [
  {
    id: 'local',
    name: 'Local snapshot graph',
    short: 'Default. Offline snapshots stored inside the project.',
    description: 'Builds and keeps a project-local graph snapshot on disk. Works with API providers or CLI providers.',
    capability: 'Supports API providers and Codex/Claude CLI pipeline mode.'
  },
  {
    id: 'zep',
    name: 'Zep Cloud',
    short: 'Advanced. Use the existing hosted graph backend.',
    description: 'Uses the original Zep-backed graph workflow. Best when you explicitly want the hosted graph features.',
    capability: 'Requires Zep API key. CLI providers are not recommended here.'
  }
]

const selectedScenario = ref('pricing')
const selectedProvider = ref('openai')
const selectedGraphBackend = ref('local')
const wizardStepIndex = ref(0)
const files = ref([])
const loading = ref(false)
const error = ref('')
const helperMessage = ref('')
const providerError = ref('')
const providerLoading = ref(false)
const refineLoading = ref(false)
const providerStatus = ref(null)
const refinedBrief = ref('')
const lastUsageEstimate = ref(null)
const isDragOver = ref(false)
const fileInput = ref(null)
const providerForm = ref({
  model_name: '',
  base_url: '',
  api_key: '',
  executable: 'codex'
})

const brief = ref({ ...scenarios[0].defaults })

const currentScenario = computed(() => {
  return scenarios.find((scenario) => scenario.id === selectedScenario.value) || scenarios[0]
})
const currentWizardStep = computed(() => wizardSteps[wizardStepIndex.value])
const wizardNavigation = computed(() => getWizardNavigation(wizardStepIndex.value, wizardSteps.length))

const currentProvider = computed(() => {
  return providerOptions.find((provider) => provider.id === selectedProvider.value) || providerOptions[1]
})

const currentGraphBackend = computed(() => {
  return graphBackendOptions.find((backend) => backend.id === selectedGraphBackend.value) || graphBackendOptions[0]
})

const simulationRequirement = computed(() => {
  const sections = [
    ['Scenario', brief.value.scenario],
    ['Timing', brief.value.timing],
    ['Key stakeholders', brief.value.stakeholders],
    ['Main question', brief.value.mainQuestion],
    ['Success or risk to evaluate', brief.value.successRisk]
  ]

  return sections
    .filter(([, value]) => value.trim() !== '')
    .map(([label, value]) => `${label}:\n${value.trim()}`)
    .join('\n\n')
})

const finalSimulationRequirement = computed(() => {
  return refinedBrief.value.trim() || simulationRequirement.value
})

const providerConfig = computed(() => {
  const config = {
    provider_type: selectedProvider.value
  }

  if (providerForm.value.model_name.trim()) {
    config.model_name = providerForm.value.model_name.trim()
  }
  if (currentProvider.value.requiresBaseUrl && providerForm.value.base_url.trim()) {
    config.base_url = providerForm.value.base_url.trim()
  }
  if (currentProvider.value.usesExecutable && providerForm.value.executable.trim()) {
    config.executable = providerForm.value.executable.trim()
  }

  return config
})

const providerSupportsPipeline = computed(() => {
  if (!currentProvider.value.supportsPipeline) {
    return false
  }
  if (selectedGraphBackend.value === 'zep' && ['codex_cli', 'claude_code_cli'].includes(selectedProvider.value)) {
    return false
  }
  return true
})

const canSubmit = computed(() => {
  return finalSimulationRequirement.value.trim() !== ''
    && files.value.length > 0
    && providerSupportsPipeline.value
    && providerIsReadyForPipeline.value
})

const canAdvanceCurrentStep = computed(() => {
  switch (currentWizardStep.value.id) {
    case 'scenario':
      return true
    case 'graph':
      return true
    case 'provider':
      return providerIsReadyForPipeline.value
    case 'documents':
      return files.value.length > 0
    case 'brief':
      return canSubmit.value
    default:
      return false
  }
})

const briefHasContent = computed(() => {
  return Object.values(brief.value).some((value) => value.trim() !== '')
})

const providerCanValidate = computed(() => {
  if (currentProvider.value.requiresApiKey) {
    return Boolean(providerForm.value.api_key.trim())
  }
  return true
})

const providerCanRefine = computed(() => {
  if (!currentProvider.value.supportsRefinement) {
    return false
  }
  if (currentProvider.value.requiresApiKey) {
    return Boolean(providerForm.value.api_key.trim()) && Boolean(providerForm.value.model_name.trim())
  }
  return true
})

const providerIsReadyForPipeline = computed(() => {
  if (!providerSupportsPipeline.value) {
    return false
  }
  if (currentProvider.value.requiresApiKey && !providerForm.value.api_key.trim()) {
    return false
  }
  if (currentProvider.value.requiresModel && !providerForm.value.model_name.trim()) {
    return false
  }
  if (currentProvider.value.requiresBaseUrl && !providerForm.value.base_url.trim()) {
    return false
  }
  return true
})

const providerStatusText = computed(() => {
  if (!providerStatus.value) {
    return ''
  }
  const health = providerStatus.value.healthcheck || {}
  if (health.message) {
    return health.message
  }
  if (health.executable_path) {
    return `Executable found at ${health.executable_path}`
  }
  if (health.model_name) {
    return `Ready with model ${health.model_name}`
  }
  return 'Provider check completed.'
})

const providerTelemetry = computed(() => {
  const health = providerStatus.value?.healthcheck || {}
  const items = []

  if (health.version) {
    items.push(`CLI version: ${health.version}`)
  }
  if (health.billing_owner) {
    items.push(`Billing owner: ${health.billing_owner}`)
  }
  if (health.usage_reporting === 'not_available') {
    items.push('Exact token and cost reporting is not currently available for this CLI integration.')
  }
  if (health.usage_reporting_note) {
    items.push(health.usage_reporting_note)
  }

  return items
})

function selectScenario(id) {
  if (id === selectedScenario.value) {
    return
  }

  if (briefHasContent.value && !window.confirm('Switch scenario template and replace the current brief?')) {
    return
  }

  selectedScenario.value = id
  const scenario = scenarios.find((item) => item.id === id)
  if (scenario) {
    brief.value = { ...scenario.defaults }
    helperMessage.value = ''
  }
}

function selectWizardStep(index) {
  wizardStepIndex.value = index
}

function goToNextWizardStep() {
  if (!canAdvanceCurrentStep.value) return
  wizardStepIndex.value = Math.min(wizardStepIndex.value + 1, wizardSteps.length - 1)
}

function goToPreviousWizardStep() {
  wizardStepIndex.value = Math.max(wizardStepIndex.value - 1, 0)
}

function selectProvider(id) {
  selectedProvider.value = id
  providerError.value = ''
  providerStatus.value = null
  refinedBrief.value = ''
  lastUsageEstimate.value = null

  if (id === 'codex_cli') {
    providerForm.value.executable = 'codex'
    providerForm.value.model_name = ''
    providerForm.value.base_url = ''
    providerForm.value.api_key = ''
  } else if (id === 'claude_code_cli') {
    providerForm.value.executable = 'claude'
    providerForm.value.model_name = ''
    providerForm.value.base_url = ''
    providerForm.value.api_key = ''
  } else if (id === 'openai') {
    providerForm.value.executable = 'codex'
    providerForm.value.base_url = ''
  } else if (id === 'anthropic') {
    providerForm.value.executable = 'codex'
    providerForm.value.base_url = ''
  }
}

function selectGraphBackend(id) {
  selectedGraphBackend.value = id
  helperMessage.value = ''
  providerError.value = ''
  providerStatus.value = null

  if (id === 'zep' && ['codex_cli', 'claude_code_cli'].includes(selectedProvider.value)) {
    helperMessage.value = 'Codex CLI and Claude Code CLI are supported in local graph mode. Switch back to the local backend or choose an API provider for Zep.'
  }
}

function triggerFileInput() {
  if (!loading.value) {
    fileInput.value?.click()
  }
}

function handleFileSelect(event) {
  const selectedFiles = Array.from(event.target.files || [])
  addFiles(selectedFiles)
}

function handleDragOver() {
  if (!loading.value) {
    isDragOver.value = true
  }
}

function handleDragLeave() {
  isDragOver.value = false
}

function handleDrop(event) {
  isDragOver.value = false
  if (loading.value) return

  const droppedFiles = Array.from(event.dataTransfer.files || [])
  addFiles(droppedFiles)
}

function addFiles(newFiles) {
  const validFiles = newFiles.filter((file) => {
    const ext = file.name.split('.').pop()?.toLowerCase()
    return ['pdf', 'md', 'txt'].includes(ext)
  })
  files.value.push(...validFiles)
}

function removeFile(index) {
  files.value.splice(index, 1)
}

async function runProviderCheck() {
  try {
    providerLoading.value = true
    providerError.value = ''
    helperMessage.value = ''
    const response = await validateProvider({
      llm_config: providerConfig.value,
      api_key: providerForm.value.api_key.trim() || undefined
    })
    providerStatus.value = response.data
    helperMessage.value = 'Provider check completed.'
  } catch (err) {
    providerError.value = err.message || 'Provider check failed.'
  } finally {
    providerLoading.value = false
  }
}

async function runBriefRefinement() {
  try {
    refineLoading.value = true
    providerError.value = ''
    helperMessage.value = ''
    const response = await refineBrief({
      llm_config: providerConfig.value,
      api_key: providerForm.value.api_key.trim() || undefined,
      brief_input: {
        scenario_type: currentScenario.value.name,
        draft_brief: simulationRequirement.value
      }
    })
    refinedBrief.value = response.data?.refined_brief || ''
    lastUsageEstimate.value = response.data?.usage_estimate || null
    helperMessage.value = refinedBrief.value ? 'Brief refined. The refined version will be used for the next run.' : 'No refined brief was returned.'
  } catch (err) {
    providerError.value = err.message || 'Brief refinement failed.'
  } finally {
    refineLoading.value = false
  }
}

function clearRefinedBrief() {
  refinedBrief.value = ''
  lastUsageEstimate.value = null
  helperMessage.value = ''
}

function formatNumber(value) {
  if (typeof value !== 'number') {
    return '0'
  }
  return new Intl.NumberFormat('en-US').format(value)
}

function formatUsd(value) {
  if (typeof value !== 'number') {
    return 'Unavailable'
  }
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 4,
    maximumFractionDigits: 4
  }).format(value)
}

function startSimulation() {
  if (!canSubmit.value || loading.value) return

  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(
      files.value,
      finalSimulationRequirement.value,
      selectedGraphBackend.value,
      providerConfig.value,
      providerForm.value.api_key.trim()
    )
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}

function runInstantDemo() {
  if (loading.value) return

  const demo = getInstantDemoConfig()
  const demoFiles = demo.documents.map((doc) => new File([doc.content], doc.name, { type: doc.type }))

  selectedScenario.value = 'launch'
  selectedGraphBackend.value = demo.graphBackend
  selectedProvider.value = demo.llmConfig.provider_type
  providerForm.value.executable = demo.llmConfig.executable
  providerForm.value.model_name = demo.llmConfig.model_name || ''
  providerForm.value.base_url = ''
  providerForm.value.api_key = ''
  providerError.value = ''
  providerStatus.value = null
  refinedBrief.value = ''
  helperMessage.value = `Loaded instant demo: ${demo.title}`
  files.value = demoFiles

  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(
      demoFiles,
      demo.simulationRequirement,
      demo.graphBackend,
      demo.llmConfig,
      ''
    )
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}

function runQuickProductLaunchDemo() {
  if (loading.value) return

  const demo = getQuickProductLaunchDemoConfig()
  const demoFiles = demo.documents.map((doc) => new File([doc.content], doc.name, { type: doc.type }))

  selectedScenario.value = 'launch'
  selectedGraphBackend.value = demo.graphBackend
  selectedProvider.value = demo.llmConfig.provider_type
  providerForm.value.executable = demo.llmConfig.executable
  providerForm.value.model_name = demo.llmConfig.model_name || ''
  providerForm.value.base_url = ''
  providerForm.value.api_key = ''
  providerError.value = ''
  providerStatus.value = null
  refinedBrief.value = ''
  helperMessage.value = `Loaded quick product launch demo: ${demo.title}`
  files.value = demoFiles

  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(
      demoFiles,
      demo.simulationRequirement,
      demo.graphBackend,
      demo.llmConfig,
      ''
    )
    router.push({
      name: 'Process',
      params: { projectId: 'new' }
    })
  })
}
</script>

<style scoped>
:root {
  --black: #000000;
  --white: #ffffff;
  --orange: #ff5a1f;
  --gray-light: #f5f5f5;
  --gray-soft: #faf8f4;
  --gray-text: #666666;
  --border: #e5e5e5;
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Space Grotesk', system-ui, sans-serif;
}

.home-container {
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(255, 90, 31, 0.08), transparent 28%),
    linear-gradient(180deg, #fffefb 0%, #ffffff 30%);
  font-family: var(--font-sans);
  color: var(--black);
}

.navbar {
  min-height: 72px;
  background: rgba(9, 21, 31, 0.96);
  color: var(--white);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 18px 40px rgba(8, 24, 34, 0.12);
}

.nav-brand-block {
  display: flex;
  align-items: center;
  gap: 14px;
}

.nav-brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.18);
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.1rem;
}

.nav-subbrand {
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.62);
}

.github-link {
  color: var(--white);
  text-decoration: none;
  font-family: var(--font-mono);
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 44px 32px 72px;
}

.hero-section {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 40px;
  align-items: center;
  margin-bottom: 48px;
}

.full-width-demo {
  grid-column: 1 / -1;
  margin-top: 12px;
}

.tag-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.orange-tag {
  background: linear-gradient(135deg, #ff7a36 0%, #d95f33 100%);
  color: var(--white);
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.version-text {
  color: #6a747a;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  border: 1px solid rgba(16, 59, 82, 0.12);
  border-radius: 999px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.84);
}

.main-title {
  margin: 0;
  font-size: clamp(3rem, 7vw, 5rem);
  line-height: 0.92;
  letter-spacing: -0.06em;
  max-width: 780px;
}

.gradient-text {
  display: block;
  background: linear-gradient(90deg, #071f2f 0%, #124d5f 58%, #e07741 120%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  margin: 24px 0;
  max-width: 640px;
  color: var(--gray-text);
  font-size: 1.05rem;
  line-height: 1.8;
}

.hero-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-points span {
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.85);
  border-radius: 999px;
  padding: 10px 14px;
  font-size: 0.9rem;
}

.trust-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 24px;
}

.trust-card {
  border: 1px solid rgba(16, 59, 82, 0.1);
  border-radius: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(247, 250, 252, 0.94) 100%);
  padding: 16px;
  min-height: 114px;
}

.trust-value {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 8px;
  color: #0f3148;
}

.trust-label {
  color: var(--gray-text);
  line-height: 1.55;
  font-size: 0.9rem;
}

.demo-callout {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 18px;
  align-items: center;
  margin-top: 22px;
  padding: 20px 22px;
  border-radius: 24px;
  border: 1px solid rgba(16, 59, 82, 0.12);
  background:
    radial-gradient(circle at top right, rgba(240, 139, 82, 0.16), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(247, 250, 252, 0.96) 100%);
}

.demo-callout-copy {
  display: grid;
  gap: 8px;
}

.demo-eyebrow {
  font-family: var(--font-mono);
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #b2542b;
}

.demo-title {
  font-size: 1.08rem;
  font-weight: 800;
  color: #0f3148;
}

.demo-text {
  color: var(--gray-text);
  line-height: 1.65;
  font-size: 0.94rem;
  max-width: 620px;
}

.instant-demo-btn {
  border: none;
  border-radius: 18px;
  background: linear-gradient(135deg, #0c2333 0%, #125f67 58%, #e07842 100%);
  color: white;
  font-size: 0.95rem;
  font-weight: 800;
  padding: 16px 18px;
  display: inline-flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  box-shadow: 0 18px 36px rgba(17, 44, 60, 0.18);
}

.instant-demo-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.instant-demo-btn.secondary {
  background: linear-gradient(135deg, #d95f33 0%, #f3b06b 60%);
}

.demo-callout-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.demo-callout-note {
  font-size: 0.85rem;
  color: var(--gray-text);
  margin-top: 10px;
}

.hero-logo-wrap {
  display: flex;
  justify-content: flex-end;
}

.hero-visual-card {
  border: 1px solid rgba(16, 59, 82, 0.12);
  border-radius: 32px;
  padding: 20px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95) 0%, rgba(243, 248, 250, 0.95) 100%);
  box-shadow: 0 28px 60px rgba(17, 44, 60, 0.12);
}

.hero-logo {
  width: 100%;
  display: block;
}

.visual-caption {
  display: grid;
  gap: 8px;
  margin-top: 16px;
  padding: 16px 18px 4px;
}

.visual-title {
  font-size: 1rem;
  font-weight: 700;
  color: #0f3148;
}

.visual-copy {
  color: var(--gray-text);
  line-height: 1.65;
  font-size: 0.94rem;
}

.dashboard-section {
  display: block;
}

.right-panel {
  border: 1px solid rgba(16, 59, 82, 0.08);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(8px);
  box-shadow: 0 20px 50px rgba(17, 44, 60, 0.06);
}

.wizard-overview-card {
  border: 1px solid var(--border);
  border-radius: 24px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfaf7 100%);
  padding: 22px;
}

.panel-header,
.steps-header,
.console-header,
.preview-header,
.assist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.panel-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  text-transform: uppercase;
  color: #7b7b7b;
}

.status-dot,
.diamond-icon {
  color: var(--orange);
}

.section-title {
  margin: 18px 0 10px;
  font-size: 1.8rem;
}

.section-desc {
  margin: 0 0 20px;
  color: var(--gray-text);
  line-height: 1.7;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.metric-card,
.guidance-card,
.checklist-card,
.assist-card,
.brief-preview {
  border: 1px solid var(--border);
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff 0%, #fbfaf7 100%);
}

.metric-card {
  padding: 16px;
}

.metric-value {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 0.9rem;
  color: var(--gray-text);
  line-height: 1.5;
}

.steps-container {
  border-top: 1px solid var(--border);
  padding-top: 20px;
}

.wizard-rail {
  margin-top: 8px;
}

.steps-header {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  text-transform: uppercase;
  color: #7b7b7b;
  margin-bottom: 14px;
}

.workflow-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.workflow-item {
  display: grid;
  grid-template-columns: 42px 1fr;
  gap: 14px;
}

.wizard-step-item {
  width: 100%;
  border: 1px solid var(--border);
  border-radius: 18px;
  background: #fff;
  padding: 14px;
  text-align: left;
  cursor: pointer;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
}

.wizard-step-item:hover,
.wizard-step-item.active {
  border-color: #0f6a73;
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(16, 59, 82, 0.08);
  background: linear-gradient(180deg, #ffffff 0%, #f5fbfc 100%);
}

.step-num {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #fff3ee;
  color: var(--orange);
  font-family: var(--font-mono);
  font-weight: 700;
}

.step-title {
  font-weight: 700;
  margin-bottom: 6px;
}

.step-desc {
  color: var(--gray-text);
  line-height: 1.6;
  font-size: 0.95rem;
}

.console-box {
  padding: 28px;
}

.wizard-full-width {
  width: 100%;
}

.wizard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 20px;
}

.wizard-title {
  font-size: 1.55rem;
  font-weight: 700;
  color: #111111;
  margin-top: 8px;
}

.wizard-progress {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  color: #7b7b7b;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 10px 12px;
  white-space: nowrap;
}

.onboarding-step,
.console-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.console-label {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  text-transform: uppercase;
  color: #1a1a1a;
}

.console-meta,
.assist-copy,
.guidance-copy {
  color: var(--gray-text);
  font-size: 0.9rem;
}

.console-divider {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 22px 0;
  color: #878787;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  text-transform: uppercase;
}

.console-divider::before,
.console-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.scenario-grid,
.assist-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.scenario-card {
  border: 1px solid var(--border);
  border-radius: 18px;
  background: white;
  padding: 18px;
  text-align: left;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
}

.scenario-card:hover,
.scenario-card.active {
  border-color: #0f6a73;
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(16, 59, 82, 0.08);
}

.scenario-name {
  font-weight: 700;
}

.scenario-copy {
  color: var(--gray-text);
  line-height: 1.55;
  font-size: 0.92rem;
}

.guidance-card {
  padding: 18px;
}

.intro-guidance {
  margin-bottom: 14px;
}

.guidance-title {
  font-weight: 700;
  margin-bottom: 8px;
}

.guidance-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.guidance-list span {
  background: #fff3ee;
  color: #9b3f18;
  border-radius: 999px;
  padding: 7px 10px;
  font-size: 0.82rem;
}

.upload-zone {
  min-height: 180px;
  border: 1.5px dashed #d6d0c8;
  border-radius: 22px;
  background: var(--gray-soft);
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.upload-zone.drag-over {
  border-color: var(--orange);
  background: #fff1ea;
}

.upload-placeholder {
  text-align: center;
  color: var(--gray-text);
}

.upload-icon {
  font-size: 1.8rem;
  color: var(--orange);
  margin-bottom: 10px;
}

.upload-title {
  color: var(--black);
  font-weight: 700;
  margin-bottom: 6px;
}

.file-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.file-item {
  display: grid;
  grid-template-columns: 42px 1fr 32px;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: white;
}

.file-icon {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--orange);
  font-weight: 700;
}

.file-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-btn,
.copy-btn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: var(--font-mono);
}

.checklist-card,
.assist-card,
.brief-preview {
  padding: 18px;
}

.checklist-title,
.preview-title,
.assist-title {
  font-weight: 700;
}

.provider-grid {
  margin-bottom: 14px;
}

.provider-guidance {
  margin-bottom: 14px;
}

.provider-telemetry .guidance-list {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.provider-fields {
  margin-bottom: 14px;
}

.provider-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.secondary-btn {
  border: 1px solid var(--border);
  background: white;
  border-radius: 14px;
  padding: 12px 16px;
  font-weight: 700;
  cursor: pointer;
}

.secondary-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.ghost-btn {
  background: transparent;
}

.checklist-card ul {
  margin: 12px 0 0;
  padding-left: 18px;
  color: var(--gray-text);
  line-height: 1.7;
}

.structured-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group span {
  font-weight: 700;
  font-size: 0.92rem;
}

.input-group input,
.input-group textarea {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px 14px;
  font-family: inherit;
  font-size: 0.95rem;
}

.input-group input {
  min-height: 48px;
}

.input-group textarea {
  resize: vertical;
  min-height: 92px;
}

.input-group.full-width {
  grid-column: 1 / -1;
}

.brief-preview pre {
  margin: 14px 0 0;
  white-space: pre-wrap;
  line-height: 1.7;
  font-family: var(--font-mono);
  font-size: 0.84rem;
  color: #303030;
}

.model-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 8px 12px;
  background: #111111;
  color: white;
  font-family: var(--font-mono);
  font-size: 0.72rem;
}

.btn-section {
  margin-top: 18px;
  gap: 10px;
}

.wizard-actions {
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(0, 1.1fr);
  gap: 12px;
}

.wizard-nav-btn {
  border: none;
  border-radius: 18px;
  font-size: 1rem;
  font-weight: 700;
  padding: 18px 22px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  min-height: 62px;
}

.wizard-nav-btn.primary {
  background: linear-gradient(90deg, #000000 0%, #262626 70%, #ff5a1f 150%);
  color: white;
}

.wizard-nav-btn.secondary {
  border: 1px solid var(--border);
  background: linear-gradient(180deg, #ffffff 0%, #f7f5f2 100%);
  color: #111111;
}

.wizard-nav-btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.start-engine-btn {
  border: none;
  border-radius: 18px;
  background: linear-gradient(90deg, #000000 0%, #262626 70%, #ff5a1f 150%);
  color: white;
  font-size: 1rem;
  font-weight: 700;
  padding: 18px 22px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.start-engine-btn:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.error-text {
  margin: 0;
  color: #c53929;
  font-size: 0.9rem;
}

.helper-text {
  margin: 0;
  color: #5c5c5c;
  font-size: 0.88rem;
}

@media (max-width: 1100px) {
  .hero-section,
  .dashboard-section {
    grid-template-columns: 1fr;
  }

  .hero-logo-wrap {
    justify-content: flex-start;
  }

  .trust-row {
    grid-template-columns: 1fr;
  }

  .demo-callout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .navbar,
  .main-content {
    padding-left: 18px;
    padding-right: 18px;
  }

  .scenario-grid,
  .assist-grid,
  .structured-grid,
  .metrics-row {
    grid-template-columns: 1fr;
  }

  .wizard-actions {
    grid-template-columns: 1fr;
  }

  .nav-brand-block {
    gap: 10px;
  }

  .nav-subbrand {
    display: none;
  }
}
</style>
