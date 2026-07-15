<!--Community Post Edit Form-->
<template>
  <div class="post-form">
    <h2 class="form-title">게시글 수정</h2>

    <div class="form-group">
      <label>제목</label>
      <input v-model="form.title" type="text" />
    </div>

    <div class="form-group">
      <label>내용</label>
      <textarea v-model="form.content" rows="8"></textarea>
    </div>

    <div class="form-actions">
      <button class="btn-submit" @click="submitForm">수정</button>
      <button class="btn-cancel" @click="$emit('cancel')">취소</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CommunityPostEditForm',
  props: {
    post: {
      type: Object,
      required: true,
    },
  },
  emits: ['submit', 'cancel'],
  data() {
    return {
      form: {
        title: '',
        content: '',
      },
    };
  },
  watch: {
    post: {
      immediate: true,
      handler(newPost) {
        this.form.title = newPost?.title ?? '';
        this.form.content = newPost?.content ?? '';
      },
    },
  },
  methods: {
    submitForm() {
    if (!this.form.title.trim() || !this.form.content.trim()) {
      alert('제목과 내용을 입력해주세요.');
      return;
    }
    
    this.$emit('submit', this.post.post_id, {
      title: this.form.title.trim(),
      content: this.form.content.trim(),
      password: this.post.password, 
    });
  },
  },
};
</script>

<style scoped>
.post-form { padding: 24px; }
.form-title { font-size: 24px; font-weight: 700; margin-bottom: 20px; }
.form-group { display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }
.form-group label { font-size: 14px; font-weight: 600; color: #222222; }
.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-group textarea { resize: vertical; }
.form-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 20px; }
.btn-submit,
.btn-cancel {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.btn-submit { background-color: #00aeef; color: white; }
.btn-cancel { background-color: #e5e7eb; color: #222222; }
</style>