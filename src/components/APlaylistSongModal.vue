<template>
  <a-modal :value="value" @input="$emit('input', $event)">
    <div style="padding:30px">
      <a-playlist-song :song="song" @song-added="$emit('song-added')"/>
    </div>
  </a-modal>
</template>

<script>
import AModal from '@/components/AModal'
import APlaylistSong from '@/components/APlaylistSong'

export default {
  components: {
    AModal,
    APlaylistSong
  },
  props: {
    song: Number,
    value: Boolean
  }
}
</script>

<style>

</style>
