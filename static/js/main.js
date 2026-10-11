/* Portfolio - mobile menu, mouse glow, loot box */
const burger = document.getElementById('burger');
const links = document.getElementById('navLinks');
burger.addEventListener('click', () => links.classList.toggle('open'));
links.addEventListener('click', e => { if (e.target.matches('a')) links.classList.remove('open'); });

// glow that follows the mouse
const glow = document.getElementById('glow');
window.addEventListener('pointermove', e => {
  glow.style.left = e.clientX + 'px';
  glow.style.top = e.clientY + 'px';
});

// loot box on the home page: pick a random thing from my profile
const chest = document.getElementById('chest');
if (chest) {
  const loot = JSON.parse(document.getElementById('lootData').textContent);
  const box = document.getElementById('lootResult');
  const rarityEl = document.getElementById('lootRarity');
  const textEl = document.getElementById('lootText');
  const subEl = document.getElementById('lootSub');
  const btn = document.getElementById('lootBtn');
  const countEl = document.getElementById('lootCount');
  let opened = 0;

  function rollRarity() {
    const n = Math.random() * 100;
    if (n < 55) return 'common';   // hobbies
    if (n < 90) return 'rare';     // skills
    return 'epic';                 // favorite sayings
  }

  function openBox() {
    chest.classList.remove('shake');
    void chest.offsetWidth;        // restart the shake animation
    chest.classList.add('shake');

    setTimeout(() => {
      const rarity = rollRarity();
      const item = loot[rarity][Math.floor(Math.random() * loot[rarity].length)];
      if (rarity === 'common') {
        rarityEl.textContent = 'COMMON · HOBBY';
        textEl.textContent = 'I love ' + item;
        subEl.textContent = '';
      } else if (rarity === 'rare') {
        rarityEl.textContent = 'RARE · SKILL UNLOCKED';
        textEl.textContent = item[0];
        subEl.textContent = 'Skill level: ' + item[1] + '%';
      } else {
        rarityEl.textContent = 'EPIC · FAVORITE SAYING';
        textEl.textContent = '“' + item[0] + '”';
        subEl.textContent = '— ' + item[1];
      }
      box.className = 'loot-result ' + rarity;
      void box.offsetWidth;
      box.classList.add('pop');
      opened++;
      btn.textContent = 'Open another';
      countEl.textContent = 'Boxes opened: ' + opened;
    }, 450);
  }

  chest.addEventListener('click', openBox);
  btn.addEventListener('click', openBox);
}
