package com.envmonitor.adapters

import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.cardview.widget.CardView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.envmonitor.R
import com.envmonitor.models.ParameterCardItem
import com.envmonitor.ui.parameter.ParameterDetailActivity

/**
 * Adapter dành cho hiển thị danh sách thẻ thông số môi trường
 */
class ParameterAdapter(
    private val context: Context
) : RecyclerView.Adapter<ParameterAdapter.ParameterViewHolder>() {

    private val items = mutableListOf<ParameterCardItem>()

    /**
     * Cập nhật danh sách các mục
     * 
     * @param newItems Danh sách mục mới
     */
    fun updateItems(newItems: List<ParameterCardItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ParameterViewHolder {
        val view = LayoutInflater.from(context)
            .inflate(R.layout.item_parameter_card, parent, false)
        return ParameterViewHolder(view)
    }

    override fun onBindViewHolder(holder: ParameterViewHolder, position: Int) {
        val item = items[position]
        holder.bind(item)
    }

    override fun getItemCount(): Int = items.size

    /**
     * ViewHolder dành cho mục thẻ thông số
     */
    inner class ParameterViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val cardContainer: CardView = itemView.findViewById(R.id.card_container)
        private val parameterName: TextView = itemView.findViewById(R.id.parameter_name)
        private val parameterStatus: TextView = itemView.findViewById(R.id.parameter_status)
        private val parameterValue: TextView = itemView.findViewById(R.id.parameter_value)
        private val parameterUnit: TextView = itemView.findViewById(R.id.parameter_unit)

        /**
         * Đặt dữ liệu cho thẻ thông số
         */
        fun bind(item: ParameterCardItem) {
            parameterName.text = item.name
            parameterStatus.text = item.statusText
            parameterValue.text = formatValue(item.value)
            parameterUnit.text = item.unit

            // Đặt màu nền và văn bản theo trạng thái
            when (item.status) {
                "normal" -> {
                    parameterStatus.setBackgroundColor(ContextCompat.getColor(context, R.color.status_normal))
                    parameterStatus.setTextColor(Color.WHITE)
                }
                "warning" -> {
                    parameterStatus.setBackgroundColor(ContextCompat.getColor(context, R.color.status_warning))
                    // Trạng thái "Trung bình" nên dùng màu văn bản đen để dễ đọc trên nền vàng
                    parameterStatus.setTextColor(Color.BLACK)
                }
                "kém" -> {
                    parameterStatus.setBackgroundColor(ContextCompat.getColor(context, R.color.status_kem))
                    parameterStatus.setTextColor(Color.WHITE)
                }
                "danger" -> {
                    parameterStatus.setBackgroundColor(ContextCompat.getColor(context, R.color.status_danger))
                    parameterStatus.setTextColor(Color.WHITE)
                }
                "offline" -> {
                    parameterStatus.setBackgroundColor(ContextCompat.getColor(context, R.color.disconnected))
                    parameterStatus.setTextColor(Color.WHITE)
                }
            }

            // Xử lý sự kiện khi nhấn vào thẻ
            cardContainer.setOnClickListener {
                val intent = Intent(context, ParameterDetailActivity::class.java).apply {
                    putExtra(ParameterDetailActivity.EXTRA_PARAMETER_ID, item.id)
                    putExtra(ParameterDetailActivity.EXTRA_PARAMETER_NAME, item.name)
                }
                context.startActivity(intent)
            }
        }

        /**
         * Định dạng giá trị số
         */
        private fun formatValue(value: Double): String {
            return if (value == value.toInt().toDouble()) {
                value.toInt().toString()
            } else {
                String.format("%.1f", value)
            }
        }
    }
}