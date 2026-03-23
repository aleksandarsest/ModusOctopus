<template>
  <div class="home-container">
    <nav class="navbar">
      <div class="nav-brand">MIROFISH</div>
      <div class="nav-links">
        <a href="https://github.com/666ghj/MiroFish" target="_blank" class="github-link">
          View on GitHub <span class="arrow">↗</span>
        </a>
      </div>
    </nav>

    <main class="main-content">
      <section class="hero-section">
        <div class="hero-copy">
          <div class="tag-row">
            <span class="orange-tag">English OSS v1</span>
            <span class="version-text">Business scenario simulation</span>
          </div>

          <h1 class="main-title">
            Test a business decision
            <span class="gradient-text">before you make it</span>
          </h1>

          <p class="hero-desc">
            Upload source documents, define the scenario, and let MiroFish build a graph,
            prepare agents, run the simulation, and generate a report you can inspect.
          </p>

          <div class="hero-points">
            <span>Graph from source material</span>
            <span>Multi-agent simulation</span>
            <span>Decision report at the end</span>
          </div>
        </div>

        <div class="hero-logo-wrap">
          <img src="../assets/logo/MiroFish_logo_left.jpeg" alt="MiroFish Logo" class="hero-logo" />
        </div>
      </section>

      <section class="dashboard-section">
        <aside class="left-panel">
          <div class="panel-header">
            <span class="status-dot">■</span> Recommended workflow
          </div>

          <h2 class="section-title">Idiot-proof onboarding</h2>
          <p class="section-desc">
            Pick a scenario, upload the evidence, structure the brief, and run the
            current MiroFish pipeline without guessing what the system expects.
          </p>

          <div class="metrics-row">
            <div class="metric-card">
              <div class="metric-value">2-10 docs</div>
              <div class="metric-label">Best input range for a first run</div>
            </div>
            <div class="metric-card">
              <div class="metric-value">Optional agents</div>
              <div class="metric-label">Use Codex or Claude Code to refine the brief</div>
            </div>
          </div>

          <div class="steps-container">
            <div class="steps-header">
              <span class="diamond-icon">◇</span> What happens next
            </div>

            <div class="workflow-list">
              <div class="workflow-item">
                <span class="step-num">01</span>
                <div class="step-info">
                  <div class="step-title">Build scenario graph</div>
                  <div class="step-desc">Extract entities, relationships, and context from your source material.</div>
                </div>
              </div>

              <div class="workflow-item">
                <span class="step-num">02</span>
                <div class="step-info">
                  <div class="step-title">Prepare simulation agents</div>
                  <div class="step-desc">Create agent profiles and simulation settings from the graph.</div>
                </div>
              </div>

              <div class="workflow-item">
                <span class="step-num">03</span>
                <div class="step-info">
                  <div class="step-title">Run the simulation</div>
                  <div class="step-desc">Simulate how stakeholders may react across social-platform environments.</div>
                </div>
              </div>

              <div class="workflow-item">
                <span class="step-num">04</span>
                <div class="step-info">
                  <div class="step-title">Generate a decision report</div>
                  <div class="step-desc">Review likely narratives, risks, and next moves in one place.</div>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <section class="right-panel">
          <div class="console-box">
            <div class="onboarding-step">
              <div class="console-header">
                <span class="console-label">01 / Pick a scenario</span>
                <span class="console-meta">Choose the closest template</span>
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

            <div class="console-divider">
              <span>Add your source material</span>
            </div>

            <div class="onboarding-step">
              <div class="console-header">
                <span class="console-label">02 / Upload source documents</span>
                <span class="console-meta">PDF, Markdown, TXT</span>
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

            <div class="console-divider">
              <span>Describe the simulation</span>
            </div>

            <div class="onboarding-step">
              <div class="console-header">
                <span class="console-label">03 / Build the brief</span>
                <span class="console-meta">Use the structure below</span>
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
                  <span class="model-badge">Engine: MiroFish v1</span>
                </div>
                <pre>{{ simulationRequirement }}</pre>
              </div>
            </div>

            <div class="console-divider">
              <span>Optional agent assist</span>
            </div>

            <div class="onboarding-step">
              <div class="assist-grid">
                <div class="assist-card">
                  <div class="assist-header">
                    <span class="assist-title">Refine with Codex</span>
                    <button type="button" class="copy-btn" @click="copyPrompt(codexPrompt)">Copy</button>
                  </div>
                  <p class="assist-copy">Use your existing Codex session to tighten the brief before you run.</p>
                </div>

                <div class="assist-card">
                  <div class="assist-header">
                    <span class="assist-title">Refine with Claude Code</span>
                    <button type="button" class="copy-btn" @click="copyPrompt(claudePrompt)">Copy</button>
                  </div>
                  <p class="assist-copy">Use Claude Code to spot missing inputs or clarify the scenario framing.</p>
                </div>
              </div>
            </div>

            <div class="console-section btn-section">
              <button class="start-engine-btn" :disabled="!canSubmit || loading" @click="startSimulation">
                <span>{{ loading ? 'Preparing...' : 'Run MiroFish' }}</span>
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

const router = useRouter()

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

const selectedScenario = ref('pricing')
const files = ref([])
const loading = ref(false)
const error = ref('')
const helperMessage = ref('')
const isDragOver = ref(false)
const fileInput = ref(null)

const brief = ref({ ...scenarios[0].defaults })

const currentScenario = computed(() => {
  return scenarios.find((scenario) => scenario.id === selectedScenario.value) || scenarios[0]
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

const codexPrompt = computed(() => {
  return `Help me turn this draft into a stronger simulation brief for MiroFish.\n\nScenario type: ${currentScenario.value.name}\n\nDraft brief:\n${simulationRequirement.value || '(empty)'}\n\nPlease:\n1. Rewrite it into a sharper business scenario brief.\n2. Point out missing context or missing documents.\n3. Keep the final brief ready to paste into a simulation tool.`
})

const claudePrompt = computed(() => {
  return `I am preparing a simulation brief for MiroFish.\n\nScenario type: ${currentScenario.value.name}\n\nDraft brief:\n${simulationRequirement.value || '(empty)'}\n\nPlease help me:\n1. Identify gaps in the scenario framing.\n2. Suggest the most important missing inputs.\n3. Rewrite the brief so it is concrete, stakeholder-aware, and ready to run.`
})

const canSubmit = computed(() => {
  return simulationRequirement.value.trim() !== '' && files.value.length > 0
})

const briefHasContent = computed(() => {
  return Object.values(brief.value).some((value) => value.trim() !== '')
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

async function copyPrompt(prompt) {
  try {
    await navigator.clipboard.writeText(prompt)
    helperMessage.value = 'Prompt copied.'
  } catch (err) {
    helperMessage.value = 'Clipboard access is unavailable here. You can still copy the prompt manually from the preview.'
  }
}

function startSimulation() {
  if (!canSubmit.value || loading.value) return

  import('../store/pendingUpload.js').then(({ setPendingUpload }) => {
    setPendingUpload(files.value, simulationRequirement.value)
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
  height: 64px;
  background: var(--black);
  color: var(--white);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
}

.nav-brand {
  font-family: var(--font-mono);
  font-weight: 800;
  letter-spacing: 1px;
  font-size: 1.1rem;
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
  padding: 56px 32px 72px;
}

.hero-section {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 40px;
  align-items: center;
  margin-bottom: 48px;
}

.tag-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.orange-tag {
  background: var(--orange);
  color: var(--white);
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.version-text {
  color: #7b7b7b;
  font-family: var(--font-mono);
  font-size: 0.8rem;
}

.main-title {
  margin: 0;
  font-size: clamp(3rem, 7vw, 5rem);
  line-height: 0.95;
  letter-spacing: -0.06em;
  max-width: 720px;
}

.gradient-text {
  display: block;
  background: linear-gradient(90deg, #000000 0%, #444444 60%, #ff5a1f 140%);
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

.hero-logo-wrap {
  display: flex;
  justify-content: flex-end;
}

.hero-logo {
  width: min(100%, 520px);
}

.dashboard-section {
  display: grid;
  grid-template-columns: 0.92fr 1.08fr;
  gap: 28px;
  align-items: start;
}

.left-panel,
.right-panel {
  border: 1px solid var(--border);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(8px);
}

.left-panel {
  padding: 28px;
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
  border-color: var(--orange);
  transform: translateY(-1px);
  box-shadow: 0 12px 24px rgba(255, 90, 31, 0.08);
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

.input-group textarea {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px 14px;
  font-family: inherit;
  font-size: 0.95rem;
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
}
</style>
