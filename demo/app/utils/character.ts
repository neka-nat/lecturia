export class Character {
  static fps = 3; // animation speed
  static cols = 3;
  static rows = 3;
  static poses: Record<string, [number, number]> = {
    idle: [0, 2],
    talk: [3, 5],
    point: [6, 8],
  };

  private ctx: CanvasRenderingContext2D;
  private sprite: HTMLImageElement | null = null;
  private animId: number | null = null;
  private curPose: keyof typeof Character.poses = 'idle';

  constructor(private readonly canvas: HTMLCanvasElement) {
    const ctx = canvas.getContext('2d');
    if (!ctx) throw new Error('2D context unavailable');
    this.ctx = ctx;
    this.fit();
    // keep crisp on resize / DPR changes
    window.addEventListener('resize', () => this.fit());
  }

  /* Resize the canvas backing store to physical pixels */
  fit() {
    const { clientWidth: w, clientHeight: h } = this.canvas;
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = w * dpr;
    this.canvas.height = h * dpr;
    this.ctx.resetTransform();
    this.ctx.scale(dpr, dpr);
  }

  /* Top-left rect for a frame index in the sheet */
  private frameRect(i: number): [number, number, number, number] {
    if (!this.sprite) throw new Error('Sprite not loaded');
    const w = this.sprite.width / Character.cols;
    const h = this.sprite.height / Character.rows;
    return [(i % Character.cols) * w, Math.floor(i / Character.cols) * h, w, h];
  }

  /* Start the RAF rendering loop (idempotent) */
  private startLoop() {
    if (this.animId != null) return; // already running

    let frame = 0;
    const interval = 1000 / Character.fps;
    let last = 0;

    const loop = (t: number) => {
      this.animId = requestAnimationFrame(loop);
      if (t - last < interval || !this.sprite) return;
      last = t;

      // clear previous frame
      this.ctx.clearRect(0, 0, this.canvas.clientWidth, this.canvas.clientHeight);
      const [s, e] = Character.poses[this.curPose] ?? Character.poses.idle;
      frame = frame < s || frame > e ? s : frame + 1 > e ? s : frame + 1;

      const [sx, sy, sw, sh] = this.frameRect(frame);
      const margin = 6; // crop inward to remove outer padding (same as original)
      this.ctx.drawImage(
        this.sprite,
        sx + margin,
        sy + margin,
        sw - margin * 2,
        sh - margin * 2,
        0,
        0,
        this.canvas.clientWidth,
        this.canvas.clientHeight,
      );
    };

    this.animId = requestAnimationFrame(loop);
  }

  /* Load a sprite sheet (data-url or url) and reset pose to idle */
  async setSprite(src: string) {
    if (!src) return;
    const img = new Image();
    img.src = src;
    await img.decode();
    this.sprite = img;
    this.curPose = 'idle';
    this.startLoop();
  }

  setPose(pose: keyof typeof Character.poses) {
    this.curPose = pose in Character.poses ? pose : 'idle';
  }
}
