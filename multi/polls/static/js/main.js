// Mobile menu toggle
document.addEventListener("DOMContentLoaded", () => {
  // 初始化 Lucide 图标
  if (typeof lucide !== "undefined") {
    lucide.createIcons()
  }

  const mobileMenuBtn = document.getElementById("mobile-menu-btn")
  const mobileMenu = document.getElementById("mobile-menu")

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden")

      // Toggle icons
      if (mobileMenu.classList.contains("hidden")) {
        mobileMenuBtn.innerHTML = '<i data-lucide="menu" class="h-5 w-5"></i>'
      } else {
        mobileMenuBtn.innerHTML = '<i data-lucide="x" class="h-5 w-5"></i>'
      }

      // 重新初始化图标
      if (typeof lucide !== "undefined") {
        lucide.createIcons()
      }
    })

    // Close mobile menu when clicking on links
    const mobileLinks = mobileMenu.querySelectorAll("a")
    mobileLinks.forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.classList.add("hidden")
        mobileMenuBtn.innerHTML = '<i data-lucide="menu" class="h-5 w-5"></i>'
        if (typeof lucide !== "undefined") {
          lucide.createIcons()
        }
      })
    })
  }

  // 初始化其他功能
  initHeroCanvas()
  initTechCardsAnimation()
  initSmoothScrolling()
})

// Hero canvas animation
function initHeroCanvas() {
  const canvas = document.getElementById("hero-canvas")
  if (!canvas) return

  const ctx = canvas.getContext("2d")

  // Set canvas size
  function resizeCanvas() {
    canvas.width = canvas.offsetWidth * window.devicePixelRatio
    canvas.height = canvas.offsetHeight * window.devicePixelRatio
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
  }

  resizeCanvas()
  window.addEventListener("resize", resizeCanvas)

  // Animation variables
  const nodes = []
  const connections = []

  // Create nodes
  for (let i = 0; i < 20; i++) {
    nodes.push({
      x: Math.random() * canvas.offsetWidth,
      y: Math.random() * canvas.offsetHeight,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      radius: Math.random() * 3 + 2,
      color: ["#007BFF", "#00BCD4", "#FF4081", "#FFC107"][Math.floor(Math.random() * 4)],
      pulse: Math.random() * Math.PI * 2,
    })
  }

  // Create connections
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      if (Math.random() < 0.1) {
        connections.push({
          from: i,
          to: j,
          strength: Math.random(),
        })
      }
    }
  }

  function animate(time) {
    ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight)

    // Update and draw nodes
    nodes.forEach((node, index) => {
      // Update position
      node.x += node.vx
      node.y += node.vy

      // Bounce off edges
      if (node.x < 0 || node.x > canvas.offsetWidth) node.vx *= -1
      if (node.y < 0 || node.y > canvas.offsetHeight) node.vy *= -1

      // Keep in bounds
      node.x = Math.max(0, Math.min(canvas.offsetWidth, node.x))
      node.y = Math.max(0, Math.min(canvas.offsetHeight, node.y))

      // Update pulse
      node.pulse += 0.02

      // Draw node
      const pulseSize = Math.sin(node.pulse) * 0.5 + 1
      ctx.beginPath()
      ctx.arc(node.x, node.y, node.radius * pulseSize, 0, Math.PI * 2)
      ctx.fillStyle = node.color
      ctx.globalAlpha = 0.8
      ctx.fill()

      // Draw glow
      ctx.beginPath()
      ctx.arc(node.x, node.y, node.radius * pulseSize * 2, 0, Math.PI * 2)
      ctx.fillStyle = node.color
      ctx.globalAlpha = 0.1
      ctx.fill()
    })

    // Draw connections
    connections.forEach((connection) => {
      const fromNode = nodes[connection.from]
      const toNode = nodes[connection.to]

      const distance = Math.sqrt(Math.pow(toNode.x - fromNode.x, 2) + Math.pow(toNode.y - fromNode.y, 2))

      if (distance < 150) {
        ctx.beginPath()
        ctx.moveTo(fromNode.x, fromNode.y)
        ctx.lineTo(toNode.x, toNode.y)
        ctx.strokeStyle = "#007BFF"
        ctx.globalAlpha = ((150 - distance) / 150) * 0.3
        ctx.lineWidth = 1
        ctx.stroke()

        // Animated flow
        const flowPosition = (time * 0.001) % 1
        const flowX = fromNode.x + (toNode.x - fromNode.x) * flowPosition
        const flowY = fromNode.y + (toNode.y - fromNode.y) * flowPosition

        ctx.beginPath()
        ctx.arc(flowX, flowY, 2, 0, Math.PI * 2)
        ctx.fillStyle = "#00BCD4"
        ctx.globalAlpha = 0.8
        ctx.fill()
      }
    })

    ctx.globalAlpha = 1
    requestAnimationFrame(animate)
  }

  animate(0)
}

// Tech cards animation
function initTechCardsAnimation() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-in")
        }
      })
    },
    { threshold: 0.1 },
  )

  const cards = document.querySelectorAll(".tech-card")
  cards.forEach((card, index) => {
    card.style.transitionDelay = `${index * 100}ms`
    observer.observe(card)
  })
}

// Smooth scrolling for navigation links
function initSmoothScrolling() {
  const links = document.querySelectorAll('a[href^="#"]')

  links.forEach((link) => {
    link.addEventListener("click", function (e) {
      e.preventDefault()

      const targetId = this.getAttribute("href")
      const targetSection = document.querySelector(targetId)

      if (targetSection) {
        const headerHeight = 80 // Account for fixed header
        const targetPosition = targetSection.offsetTop - headerHeight

        window.scrollTo({
          top: targetPosition,
          behavior: "smooth",
        })
      }
    })
  })
}
