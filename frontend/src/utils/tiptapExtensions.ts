import { Extension, Mark, mergeAttributes } from '@tiptap/core'

export const FontSize = Extension.create({
  name: 'fontSize',
  addOptions() {
    return {
      types: ['textStyle'],
    }
  },
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          fontSize: {
            default: null,
            parseHTML: element => element.style.fontSize?.replace(/['"]+/g, ''),
            renderHTML: attributes => {
              if (!attributes.fontSize) {
                return {}
              }
              return {
                style: `font-size: ${attributes.fontSize}`,
              }
            },
          },
        },
      },
    ]
  },
  addCommands() {
    return {
      setFontSize: (fontSize: string) => ({ chain }) => {
        return chain().setMark('textStyle', { fontSize }).run()
      },
      unsetFontSize: () => ({ chain }) => {
        return chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run()
      },
    } as any
  },
})

export const LineHeight = Extension.create({
  name: 'lineHeight',
  addOptions() {
    return {
      types: ['paragraph', 'heading', 'listItem'],
    }
  },
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          lineHeight: {
            default: null,
            parseHTML: element => element.style.lineHeight || null,
            renderHTML: attributes => {
              if (!attributes.lineHeight) {
                return {}
              }
              return {
                style: `line-height: ${attributes.lineHeight}`,
              }
            },
          },
        },
      },
    ]
  },
  addCommands() {
    return {
      setLineHeight: (lineHeight: string) => ({ commands }) => {
        let applied = false
        this.options.types.forEach((type: string) => {
          if (commands.updateAttributes(type, { lineHeight })) {
            applied = true
          }
        })
        return applied
      },
      unsetLineHeight: () => ({ commands }) => {
        let applied = false
        this.options.types.forEach((type: string) => {
          if (commands.resetAttributes(type, 'lineHeight')) {
            applied = true
          }
        })
        return applied
      },
    } as any
  },
})

export const Indent = Extension.create({
  name: 'indent',
  addOptions() {
    return {
      types: ['paragraph', 'heading'],
      minIndent: 0,
      maxIndent: 8,
    }
  },
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          indent: {
            default: 0,
            parseHTML: element => {
              const padding = element.style.paddingLeft || '0px'
              return parseInt(padding) / 20 || 0
            },
            renderHTML: attributes => {
              if (!attributes.indent) {
                return {}
              }
              return {
                style: `padding-left: ${attributes.indent * 20}px`,
              }
            },
          },
        },
      },
    ]
  },
  addCommands() {
    return {
      indent: () => ({ tr, state, dispatch }) => {
        const { selection } = state
        tr.doc.nodesBetween(selection.from, selection.to, (node, pos) => {
          if (this.options.types.includes(node.type.name)) {
            const indent = (node.attrs.indent || 0) + 1
            if (indent <= this.options.maxIndent) {
              tr.setNodeMarkup(pos, node.type, { ...node.attrs, indent })
            }
          }
        })
        if (dispatch) dispatch(tr)
        return true
      },
      outdent: () => ({ tr, state, dispatch }) => {
        const { selection } = state
        tr.doc.nodesBetween(selection.from, selection.to, (node, pos) => {
          if (this.options.types.includes(node.type.name)) {
            const indent = (node.attrs.indent || 0) - 1
            if (indent >= this.options.minIndent) {
              tr.setNodeMarkup(pos, node.type, { ...node.attrs, indent })
            }
          }
        })
        if (dispatch) dispatch(tr)
        return true
      },
    } as any
  },
})

export const CommentMark = Mark.create({
  name: 'commentMark',

  addAttributes() {
    return {
      commentId: {
        default: null,
        parseHTML: element => element.getAttribute('data-comment-id'),
        renderHTML: attributes => {
          if (!attributes.commentId) {
            return {}
          }
          return {
            'data-comment-id': attributes.commentId,
            class: 'comment-highlight',
            style: 'background-color: rgba(255, 212, 0, 0.4); border-bottom: 2px solid #ffd400;',
          }
        },
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-comment-id]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes(this.options.HTMLAttributes, HTMLAttributes), 0]
  },

  addCommands() {
    return {
      setComment: (commentId: string | number) => ({ commands }) => {
        return commands.setMark(this.name, { commentId })
      },
      unsetComment: () => ({ commands }) => {
        return commands.unsetMark(this.name)
      },
      unsetSpecificComment: (commentId: string | number) => ({ tr, dispatch }) => {
        // Advanced: removing specific comments
        return true
      }
    } as any
  },
})
