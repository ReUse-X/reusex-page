// ReUseX site scripts — feature modules, bundled by Hugo's js.Build.
// The site must work without JS; these only enhance.
import { initTheme } from './theme.js';
import { initMenu } from './menu.js';
import { initBeforeAfter } from './before-after.js';
import { initVideo } from './video.js';

initTheme();
initMenu();
initBeforeAfter();
initVideo();
